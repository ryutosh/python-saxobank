from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from logging import getLogger
from typing import Optional, Tuple

from pydantic import ValidationError
from winko import exceptions

from . import ServiceState, models
from . import request as saxo_req
from . import service_state

# from pydantic import parse_obj_as

log = getLogger(__name__)


# Now supported asset types
SUPPORTED_ASSET_TYPES = [models.AssetType.CfdOnIndex]

ERROR_CODE_TRANSLATION = {"TooFarFromEntryOrder": "{OrderType} Order. "}


@dataclass
class ErrorInfo:
    error_code: str | None
    message: str | None

    # TODO! MOVE TO USER-SIDE?
    # バックエンドに、アプリケーションのためのわかりやすいメッセージを埋め込まない（UIとアプリに依存しアプリ開発側で変えられるべきであるため）
    # Problem JSONなどの仕様に沿った共通の構造を持たせるのが良い設計になります。
    # https://qiita.com/tashxii/items/573862fd432f1acab616#:~:text=%E3%83%90%E3%83%83%E3%82%AF%E3%82%A8%E3%83%B3%E3%83%89%E3%81%A7%E5%AE%9A%E7%BE%A9%E3%81%99%E3%82%8B%E5%85%B1%E9%80%9A%E3%83%95%E3%82%A9%E3%83%BC%E3%83%9E%E3%83%83%E3%83%88%E4%BE%8B
    @classmethod
    def translate(cls, request: models.OrdersRequest, response: models.ErrorInfo | None, is_related_order: bool = False):
        if not response:
            return ""

        msg = ERROR_CODE_TRANSLATION.get(response.ErrorCode, "").format(**request.dict(exclude_unset=False))
        if is_related_order:
            msg = "Related Orders failed. " + msg
        msg = msg + response.Message if response.Message else ""

    @classmethod
    def from_response(
        cls, request: models.OrdersRequest, response: models.ErrorInfo | None, is_related_order: bool = False
    ) -> ErrorInfo | None:
        return (
            cls(error_code=response.ErrorCode, message=cls.translate(request, response, is_related_order)) if response else None
        )


@dataclass
class OrderResult:
    order_id: str | None
    error_info: ErrorInfo | None
    related_orders: list[OrderResult] | None

    @classmethod
    def from_response(
        cls, request: models.OrdersRequest, response: models.OrdersResponse, is_related_order: bool = False
    ) -> OrderResult:
        return cls(
            order_id=response.OrderId,
            error_info=ErrorInfo.from_response(request, response.ErrorInfo, is_related_order),
            related_orders=[cls.from_response(req, res, True) for req, res in zip(request.Orders, response.Orders)]
            if (request.Orders and response.Orders)
            else None,
        )


LOGICAL_ERROR = ErrorInfo(None, "Winko system error. System fix needed.")


def conform_amount(ref_data: models.InstrumentsDetailsResponse, amount_orig: Decimal):
    return round(amount_orig, ref_data.AmountDecimals) if ref_data.AmountDecimals is not None else amount_orig


def conform_price_to_format(format_data: Optional[models.PriceDisplayFormatResponse], price_orig: Decimal):
    if format_data.Format and format_data.Format != models.PriceDisplayFormatType.Normal:
        # Not implemented
        raise NotImplementedError()

    return round(price_orig, format_data.OrderDecimals) if format_data.OrderDecimals else price_orig


def conform_price_to_tick_size(tick_size: Decimal, price_orig: Decimal):
    return round(price_orig / tick_size) * tick_size


def tick_size_from_scheme(scheme_data: models.TickSizeSchemeResponse, price_orig: Decimal):
    elements = sorted([] if scheme_data.Elements is None else scheme_data.Elements, key=lambda e: e.HighPrice)
    for element in elements:
        if price_orig <= element.HighPrice:
            return element.TickSize

    return scheme_data.DefaultTickSize if scheme_data.DefaultTickSize else None  # SHOULD rise error, not None


def conform_price(
    ref_data: models.InstrumentsDetailsResponse, price_orig: Decimal, order_type=models.PlaceableOrderType.Market
):
    tick_size = None

    if scheme := ref_data.TickSizeScheme:
        tick_size = tick_size_from_scheme(scheme, price_orig)

    if tick_size is None:
        tick_size = (
            ref_data.TickSizeStopOrder
            if ref_data.TickSizeStopOrder is not None and order_type.is_stop()
            else ref_data.TickSizeLimitOrder
            if ref_data.TickSizeLimitOrder is not None and order_type.is_limit()
            else ref_data.TickSize
            if ref_data.TickSize is not None
            else None
        )

    if tick_size:
        return conform_price_to_tick_size(tick_size, price_orig)

    return conform_price_to_format(ref_data.Format, price_orig)


# 　↓いまは注文UIやストラテジー注文が無いのでCheck処理をここに置いても良いが、本来ReferenceはUI入力時の補完に使われるべきだと思うので、それらが完成次第、UIやストラテジー側でReferenceをもとに注文できるよう、処理を移すべき
def check_ref(
    order_data: models.OrdersRequest, ref_data: models.InstrumentsDetailsResponse, adjust_amount=True, adjust_price=True
) -> tuple[bool, str | None]:

    # Check reference data applicable for order data
    if (order_data.AssetType and ref_data.AssetType and order_data.AssetType != ref_data.AssetType) or (
        order_data.Uic and ref_data.Uic and order_data.Uic != ref_data.Uic
    ):
        log.error(
            f"Not applicable reference data. Order Data {order_data.AssetType}/{order_data.Uic}, Ref Data {ref_data.AssetType}/{ref_data.Uic}"
        )
        return False, "Illegal condition occured."

    # Check if tradable
    if not ref_data.IsTradable:
        return False, "Not tradalbe instrument."

    # Check trading status
    if ref_data.TradingStatus != models.TradingStatus.Tradable:
        return False, f"Not tradable status. Reason: {ref_data.NonTradableReason}"

    # Check asset type is supported this system
    if order_data.AssetType and order_data.AssetType not in SUPPORTED_ASSET_TYPES:
        return False, "AssetType{order_data.AssetType} is not supported by system. Supported: {SUPPORTED_ASSET_TYPES}"

    # Check asset type is tradable
    if order_data.AssetType and ref_data.TradableAs and order_data.AssetType not in ref_data.TradableAs:
        return False, "Asset type {order_data.AssetType} is not tradable. Tradable As: {ref_data.TradableAs}"

    # Check if instrument can't be short
    if order_data.BuySell == models.BuySell.Sell and ref_data.ShortTradeDisabled:
        return False, "Check failed. Short trade is disabled"

    # Check order type supported
    if ref_data.SupportedOrderTypes and order_data.OrderType not in ref_data.SupportedOrderTypes:
        return (
            False,
            f"OrderType {order_data.OrderType} is not supported. Supported order types: {ref_data.SupportedOrderTypes}",
        )

    # Check duration type
    for order_type, duration_types in ref_data.SupportedOrderTypeSettings or []:
        if order_data.OrderType == order_type and order_data.OrderDuration.DurationType not in duration_types:
            return (
                False,
                "DurationType {order_data.OrderDuration.DurationType} is not supported for OrderType {order_data.OrderType}. Supported duration types: {duration_types}",
            )

    # Check amount conformation
    if order_data.Amount is not None:
        conformed_amount = conform_amount(ref_data, order_data.Amount)

        if adjust_amount:
            log.info(f"Order amount {order_data.Amount} conformed to {conformed_amount}")
            order_data.Amount = conformed_amount

        elif order_data.Amount != conformed_amount:
            return False, f"Check failed. Amount {order_data.Amount} is not conform."

    # Check order price conformation
    if order_data.OrderPrice is not None:
        conformed_price = conform_price(ref_data, order_data.OrderPrice, order_data.OrderType)

        if adjust_price:
            log.info(f"Order price {order_data.OrderPrice} conformed to {conformed_price}")
            order_data.OrderPrice = conformed_price

        elif order_data.OrderPrice != conformed_price:
            return False, f"Check failed. Order price {order_data.OrderPrice} is not conform."

    # Check stop limit price conformation
    if order_data.StopLimitPrice is not None:
        conformed_price = conform_price(ref_data, order_data.StopLimitPrice, order_data.OrderType)

        if adjust_price:
            log.info(f"Strop limit price {order_data.StopLimitPrice} conformed to {conformed_price}")
            order_data.StopLimitPrice = conformed_price

        elif order_data.StopLimitPrice != conformed_price:
            return False, f"Check failed. Stop limit price {order_data.StopLimitPrice} is not conform."

    return True, None


async def check_order(
    winko_id,
    order_data: models.OrdersRequest,
    ref_data: models.InstrumentsDetailsResponse = None,
    effectual_until=None,
    adjust_amount=True,
    adjust_price=True,
) -> tuple[bool, str | None]:
    log.debug(f"Checking order..")

    # No instruments, No reference
    # if not ((asset_type := order_data.AssetType) and (uic := order_data.Uic) is not None) and not ref_data:
    #     log.error(f"No instruments, no reference. Can't continue check.")
    #     raise exceptions.OrderError()

    # When instrument data, fetch reference data to check it.
    # if asset_type and uic is not None and (asset_type != ref_data.AssetType or uic != ref_data.Uic):
    if (asset_type := order_data.AssetType) and (uic := order_data.Uic) is not None:
        log.debug(f"New instrument found, need reference to check it.")

        # Make instruments reference request
        instruments_req = models.InstrumentsDetailsRequest(
            FieldGroups=[models.InstrumentFieldGroup.OrderSetting, models.InstrumentFieldGroup.SupportedOrderTypeSettings]
        ).dict(exclude_unset=True)
        path_conv = {"Uic": uic, "AssetType": asset_type}
        log.debug(f"Instruments details request with message: {instruments_req}")

        # Send instruments datails request
        try:
            status, ref_data = await saxo_req.instruments_details(winko_id, instruments_req, path_conv, effectual_until)
        except exceptions.RequestError:
            raise exceptions.OrderError()
        else:
            log.debug(f"Reference data fetched. Check using it..")

        if ref_data.ErrorCode:
            log.debug(f"Reference data contains error. abort.")
            raise exceptions.OrderError()

    # Check ordeer using ref data
    if ref_data:
        is_ok, msg = check_ref(order_data, ref_data, adjust_amount, adjust_price)
        if not is_ok:
            return is_ok, msg

    # Recursively check related orders
    for related_order in order_data.Orders or []:
        is_ok, msg = await check_order(winko_id, related_order, ref_data, effectual_until, adjust_amount, adjust_price)
        if not is_ok:
            return is_ok, msg

    log.debug(f"Check passed.")
    return True, ""


async def order_entry(winko_id, orders_main, is_entry=True, effectual_until=None, ensure_price_range=None) -> OrderResult:

    # TODO!: Check if account has authorized

    is_ok, msg = await check_order(winko_id, orders_main, effectual_until)
    if not is_ok:
        return OrderResult(error_info=ErrorInfo("", msg))

    # --------------------------
    # Check prices current
    if ensure_price_range:

        # Get instrument information
        infoprices_req = models.InfoPricesRequest(
            AssetType=orders_main.AssetType,
            Uic=orders_main.Uic,
            # FieldGroups=[models.InfoPriceGroupSpec.Quote],
            FieldGroups=[models.InfoPriceGroupSpec.PriceInfoDetails],
        ).dict(exclude_unset=True)
        log.debug(f"Infoprices request with message: {infoprices_req}")

        # Send infoprice request
        try:
            status, infoprices_res = await saxo_req.infoprices(winko_id, infoprices_req, effectual_until)
        except exceptions.RequestError:
            raise exceptions.OrderError()

        if infoprices_res.ErrorInfo or infoprices_res.PriceInfoDetails is None:
            raise exceptions.OrderError()

        # if infoprices_res.Quote.DelayedByMinutes:
        #     log.info(f"Price info delayed: {infoprices_res.Quote}")
        #     raise exceptions.OrderEnsurePriceNotGuaranteedError(
        #         market_price="can not determine", p1=ensure_price_range[0], p2=ensure_price_range[1]
        #     )

        market_price = infoprices_res.PriceInfoDetails.LastTraded
        if not market_price or not (ensure_price_range[0] <= market_price <= ensure_price_range[1]):
            log.info(f"Price not in ensured range: {infoprices_res.PriceInfoDetails}")
            raise exceptions.OrderEnsurePriceNotGuaranteedError(
                market_price=market_price, p1=ensure_price_range[0], p2=ensure_price_range[1]
            )

    # ===================================
    # Send order request
    orders_req = orders_main.dict(exclude_unset=True)

    try:
        status, orders_res = await saxo_req.orders(winko_id, orders_req, is_entry, effectual_until)
    except exceptions.RequestError:
        # CHANGE: return as normal error response
        raise exceptions.OrderError()

    log.debug(f"Ordered. Response: {orders_res}")
    # わざわざシリアライズ関数作らなくても、これでいけるのでは？
    # https://qiita.com/ttyszk/items/01934dc42cbd4f6665d2#:~:text=DataclassPerson(**dict_person1)
    # > 辞書からクラスに戻す時はアンパックを使い以下のようになります。
    # > DataclassPerson(**dict_person1)
    return OrderResult.from_response(orders_main, orders_res)


async def close(winko_id, position_id, external_reference: str = None):
    """
    Close specified position.
    Currently, close position if there were related orders or not. This may should be check these then choose abend or not.
    Now supports market order type only to reversive full-fill amount.
    """
    log.debug(f"Close positions: {position_id}")

    # Send clients request
    try:
        status, clients_res = await saxo_req.clients_me(winko_id, effectual_until=None)
    except exceptions.RequestError:
        raise exceptions.OrderError()

    # --------------------------
    # Check netting mode
    if clients_res.PositionNettingProfile != models.ClientPositionNettingProfile.FifoEndOfDay:
        raise exceptions.NotSupportedNettingModeError(profile=clients_res.PositionNettingProfile)

    # Make positions request
    path_conv = {"PositionId": position_id}
    positions_req = models.PositionsReq(
        ClientKey=clients_res.ClientKey, FieldGroups=[models.PositionFieldGroup.PositionBase]
    ).dict(exclude_unset=True)

    # Send positions request
    try:
        status, positions_res = await saxo_req.positions(winko_id, positions_req, path_conv=path_conv, effectual_until=None)
    except exceptions.RequestError:
        raise exceptions.OrderError()

    if (
        not positions_res.PositionBase
        or not (amount_signed := positions_res.PositionBase.Amount)
        or not (asset_type := positions_res.PositionBase.AssetType)
        or (uic := positions_res.PositionBase.Uic) is None
    ):
        log.error(f"Positions has fewer information. Can't continue to order Position Base:{positions_res.PositionBase}")
        raise exceptions.OrderError()

    amount = abs(amount_signed)
    buy_sell = models.BuySell.Buy if amount_signed < 0 else models.BuySell.Sell

    if positions_res.PositionBase.IsForceOpen or not positions_res.PositionBase.IsMarketOpen:
        log.debug(
            f"Can't continue to order because of Market state. ForceOpen:{positions_res.PositionBase.IsForceOpen}, MarketOpen:{positions_res.PositionBase.IsMarketOpen}"
        )
        raise exceptions.NotTradableError()

    if positions_res.PositionBase.Status != models.PositionStatus.Open:
        log.debug(f"Can't continue to order because of Position state. PositionStatus:{positions_res.PositionBase.Status}")
        raise exceptions.PositionNotFoundError(position_id=position_id)

    # Make close request
    try:
        orders_main = models.OrdersRequest(
            PositionId=position_id,
            Orders=[
                models.OrdersRequest(
                    AssetType=asset_type,
                    Uic=uic,
                    Amount=amount,
                    BuySell=buy_sell,
                    ManualOrder=False,
                    OrderType=models.PlaceableOrderType.Market,
                    OrderDuration=models.OrderDuration(DurationType=models.OrderDurationType.DayOrder),
                )
            ],
        )
        if external_reference:
            orders_main.ExternalReference = external_reference

        # if positions_res.PositionBase.AccountKey:
        #     orders_main.Orders[0].AccountKey = positions_res.PositionBase.AccountKey

    except ValidationError as ex:
        log.error(f"Orders request was not valid. Error: {ex}")
        raise exceptions.OrderError(status=None)

    order_res = await order_entry(winko_id, orders_main)

    if (
        (error_info := order_res.error_info)
        and (error_code := error_info.error_code)
        and error_code == "OrderRelatedPositionIsClosed"
    ):
        log.debug(
            f"Position related order was placed, but position was already closed. PositionStatus:{positions_res.PositionBase.Status}"
        )
        raise exceptions.PositionNotFoundError(position_id=position_id)

    return order_res


async def market(
    winko_id: str,
    asset_type: models.AssetType,
    uic: int,
    buy_sell: models.BuySell,
    quantity: Decimal,
    take_profit: Decimal = None,
    stop_loss: Decimal = None,
    stop_limit: Decimal = None,
    trailing_step: Decimal = None,
    account_key: models.AccountKey = None,
    external_reference: str = None,
    effectual_until: datetime = None,
    ensure_price_range: Tuple[Decimal, Decimal] = None,
):
    """
    Makes market order message conforming to broker platform.
    Now supports stop loss, stop limit related orders. TrailingStop is not supported.
    Now supports CfdOnIndex only.
    """

    if service_state != ServiceState.RUNNING:
        log.debug(f"Can not proceed request. Serivce State:{service_state}")
        return
    if trailing_step is not None:
        raise NotImplementedError()

    # Make order request
    orders_main = models.OrdersRequest(
        AssetType=asset_type,
        Uic=uic,
        BuySell=buy_sell,
        Amount=quantity,
        OrderType=models.PlaceableOrderType.Market,
        OrderDuration=models.OrderDuration(DurationType=models.OrderDurationType.DayOrder),
        ManualOrder=False,
    )
    if account_key:
        orders_main.AccountKey = account_key
    if external_reference:
        orders_main.ExternalReference = external_reference

    # Make related orders
    related_orders = []

    # Make stop loss or stop limit request
    if stop_loss is not None:
        orders_stop = models.OrdersRequest(
            BuySell=buy_sell.opposite(),
            OrderType=models.PlaceableOrderType.StopLimit
            if (stop_limit is not None)
            else models.PlaceableOrderType.TrailingStopIfTraded
            if (trailing_step is not None)
            else models.PlaceableOrderType.StopIfTraded,
            OrderDuration=models.OrderDuration(DurationType=models.OrderDurationType.GoodTillCancel),
            OrderPrice=stop_loss,
            # TrailingStopDistanceToMarket =
            ManualOrder=False,
        )
        if account_key:
            orders_stop.AccountKey = account_key

        if external_reference:
            orders_stop.ExternalReference = external_reference

        if stop_limit is not None:
            orders_stop.StopLimitPrice = stop_limit

        if trailing_step is not None:
            orders_stop.TrailingStopStep = trailing_step

        related_orders.append(orders_stop)

    # Set limit request
    if take_profit is not None:
        orders_limit = models.OrdersRequest(
            BuySell=buy_sell.opposite(),
            OrderType=models.PlaceableOrderType.Limit,
            OrderDuration=models.OrderDuration(DurationType=models.OrderDurationType.GoodTillCancel),
            OrderPrice=take_profit,
            ManualOrder=False,
        )
        if account_key:
            orders_limit.AccountKey = account_key

        related_orders.append(orders_limit)

    # Set related orders
    if related_orders:
        orders_main.Orders = related_orders

    # Request entry
    return await order_entry(winko_id, orders_main, True, effectual_until, ensure_price_range)


async def modify(winko_id, order_id, quantity=None, price=None, stop_limit=None, trailing_step=None):
    #    duration=None,
    """
    Modify order.
    Now support single order only. Relative order can't be accepted, but can be modified calling method for each order.
    Duration change is not supported now.
    Now support CfdOnIndex only.
    """

    # Send clients request
    try:
        status, clients_res = await saxo_req.clients_me(winko_id, effectual_until=None)
    except exceptions.RequestError:
        raise exceptions.OrderError()

    # --------------------------
    # Check netting mode
    if clients_res.PositionNettingProfile != models.ClientPositionNettingProfile.FifoEndOfDay:
        raise exceptions.NotSupportedNettingModeError(profile=clients_res.PositionNettingProfile)

    # Make portfolio order request
    port_orders_req = models.PortOrdersReq().dict(exclude_unset=True)
    path_conv = {"ClientKey": clients_res.ClientKey, "OrderId": order_id}

    # Send portfolio order request
    try:
        status, port_orders_res = await saxo_req.port_orders(winko_id, port_orders_req, path_conv, effectual_until=None)
    except exceptions.RequestError:
        raise exceptions.OrderError()

    # Make order request
    if not (order_orig := port_orders_res.find_by_order_id(order_id)):
        raise exceptions.OrderError()

    order_new = models.OrdersRequest.copy_from(order_orig)
    if quantity is not None:
        order_new.Amount = quantity
    if price is not None:
        order_new.OrderPrice = price
    if stop_limit is not None:
        order_new.StopLimitPrice = stop_limit
    if trailing_step is not None:
        order_new.TrailingStopStep = trailing_step

    # Send order request
    order_res = await order_entry(winko_id, order_new, False)

    if (error_info := order_res.error_info) and (error_code := error_info.error_code) and error_code == "OrderNotFound":
        log.debug(f"Order modification was issued, but order was not found. OrderId:{order_id}")
        raise exceptions.OrderNotFoundError(order_id=order_id)

    return order_res
