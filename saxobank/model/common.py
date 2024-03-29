from __future__ import annotations

import string
from datetime import datetime
from enum import Enum, auto, unique
from typing import Any, Optional
from uuid import uuid4


# TODO: Not full covered
class AssetType(str, Enum):
    """Asset Type.

    URL: xx

    Attributes:
        Bond (AssetType): Bond
        FxSpot (AssetType): FX traded at spot.
        CfdOnIndex (AssetType): CFD on stock indexes.
    """

    Bond = "Bond"
    FxSpot = "FxSpot"
    FxBinaryOption = "FxBinaryOption"
    FxForwards = "FxForwards"
    FxKnockInOption = "FxKnockInOption"
    FxKnockOutOption = "FxKnockOutOption"
    FxNoTouchOption = "FxNoTouchOption"
    FxOneTouchOption = "FxOneTouchOption"
    FxSwap = "FxSwap"
    CfdOnIndex = "CfdOnIndex"
    Stock = "Stock"


class AuthenticationLevel(str, Enum):
    Authenticated = "Authenticated"
    Elevated = "Elevated"


class BuySell(str, Enum):
    Buy = "Buy"
    Sell = "Sell"

    def opposite(self):
        return self.Sell if self == self.Buy else self.Buy


class ChartRequestMode(str, Enum):
    From = "From"
    UpTo = "UpTo"


class ClientPositionNettingMode(str, Enum):
    EndOfDay = "EndOfDay"
    Intraday = "Intraday"


class ClientPositionNettingProfile(str, Enum):
    AverageRealTime = "AverageRealTime"
    FifoEndOfDay = "FifoEndOfDay"
    FifoRealTime = "FifoRealTime"


class HeartbeatReason(str, Enum):
    NoNewData = "NoNewData"
    SubscriptionTemporarilyDisabled = "SubscriptionTemporarilyDisabled"
    SubscriptionPermanentlyDisabled = "SubscriptionPermanentlyDisabled"


class InfoPriceGroupSpec(str, Enum):
    # Commission fields are returned in results.
    Commissions = "Commissions"
    # Display and Format
    DisplayAndFormat = "DisplayAndFormat"
    # Fields related to the asset type are returned in results.
    # Fields in this group are only returned when issuing a GET and in the initial snapshot if setting up a subscription.
    InstrumentPriceDetails = "InstrumentPriceDetails"
    # Informational price fields are returned in results.
    PriceInfo = "PriceInfo"
    # Detailed price fields are returned in results.
    PriceInfoDetails = "PriceInfoDetails"
    # Quote data fields are returned in results.
    Quote = "Quote"


class InstrumentFieldGroup(str, Enum):
    OrderSetting = "OrderSetting"
    SupportedOrderTypeSettings = "SupportedOrderTypeSettings"
    TradingSessions = "TradingSessions"


class MarketState(str, Enum):
    Closed = "Closed"
    Open = "Open"
    PostMarket = "PostMarket"
    PreMarket = "PreMarket"
    Unknown = "Unknown"


class NonTradableReasons(str, Enum):
    _None = "None"
    ETFsWithoutKIIDs = "ETFsWithoutKIIDs"
    ExpiredInstrument = "ExpiredInstrument"
    NonShortableInstrument = "NonShortableInstrument"
    OfflineTradableBonds = "OfflineTradableBonds"
    NotOnlineClientTradable = "NotOnlineClientTradable"
    ReduceOnlyInstrument = "ReduceOnlyInstrument"
    OtherReason = "OtherReason"


class OrderDistanceType(str, Enum):
    Undefined = "Undefined"
    Percentage = "Percentage"
    Pips = "Pips"
    Price = "Price"


# https://www.developer.saxo/openapi/learn/core-business-concepts
# https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/fill-or-kill-fok/
class OrderDurationType(str, Enum):
    AtTheClose = "AtTheClose"
    AtTheOpening = "AtTheOpening"
    # The caveat is that the order is only good for, or can only be executed up until the end of, the current trading day.
    # The order is to be filled if/when the asset reaches the price specified in the order.
    # In the event that the asset does not hit the price specified in the order,
    # the order is then allowed to expire without any further action required.
    # Market orders must have OrderDuration.DurationType = DayOrder
    DayOrder = "DayOrder"
    # FOK orders require the transaction to go through immediately (usually within a few seconds),
    # to the full extent of the order, and at its set price; otherwise, the order is automatically canceled.
    # The “kill” part of the order refers to the cancellation if the order cannot be filled to its fullest extent.
    FillOrKill = "FillOrKill"
    GoodForPeriod = "GoodForPeriod"
    # A GTC transaction keeps the order open until it is either canceled or has been filled at
    # or below a specified stock price. A GTC order is used when the purchase does not need to be as immediate,
    # and the buyer can wait longer for the entirety of the order to be filled.
    GoodTillCancel = "GoodTillCancel"
    GoodTillDate = "GoodTillDate"
    # IOC order fills any part of the order it can immediately and then cancels whatever cannot be filled.
    # An IOC order can be useful if the broker does not need the entirety of the order to be filled
    # but rather wants to capitalize at a certain price point.
    ImmediateOrCancel = "ImmediateOrCancel"


class OrderFieldGroup(str, Enum):
    DisplayAndFormat = "DisplayAndFormat"
    ExchangeInfo = "ExchangeInfo"
    Greeks = "Greeks"


class OrderStatus(str, Enum):
    Unknown = "Unknown"
    # Parked orders are in inactive state, can't be filled, but remain available in so they can be made active at any time.
    # Clients can manually 'park' and 'activate' an order.
    Parked = "Parked"
    NotWorking = "NotWorking"
    NotWorkingLockedCancelPending = "NotWorkingLockedCancelPending"
    NotWorkingLockedChangePending = "NotWorkingLockedChangePending"
    Working = "Working"
    WorkingLockedCancelPending = "WorkingLockedCancelPending"
    WorkingLockedChangePending = "WorkingLockedChangePending"
    LockedPlacementPending = "LockedPlacementPending"
    Filled = "Filled"


class OrderType(str, Enum):
    Market = "Market"
    Limit = "Limit"
    Stop = "Stop"
    StopIfTraded = "StopIfTraded"
    StopLimit = "StopLimit"
    TrailingStop = "TrailingStop"
    TrailingStopIfBid = "TrailingStopIfBid"
    TrailingStopIfOffered = "TrailingStopIfOffered"
    TrailingStopIfTraded = "TrailingStopIfTraded"


# TODO: Not full covered
class PlaceableOrderType(str, Enum):
    Limit = "Limit"
    Market = "Market"
    Stop = "Stop"
    StopIfTraded = "StopIfTraded"
    StopLimit = "StopLimit"
    TrailingStop = "TrailingStop"
    TrailingStopIfTraded = "TrailingStopIfTraded"

    def is_stop(self):
        # Used to determine ticker price to conform TickerSize/TickerSizeLimitOrder/TickerSizeStopOrder
        return (
            True
            if self
            in [
                self.Stop,
                self.StopIfTraded,
                self.StopLimit,
                self.TrailingStop,
                self.TrailingStopIfTraded,
            ]
            else False
        )

    def is_limit(self):
        # Used to determine ticker price to conform TickerSize/TickerSizeLimitOrder/TickerSizeStopOrder
        return True if self in [self.Limit, self.StopLimit] else False


class PositionFieldGroup(str, Enum):
    # Trading costs associated with opening/closing a position
    Costs = "Costs"
    # Information about the instrument of the position and how to display it.
    DisplayAndFormat = "DisplayAndFormat"
    # Adds information about the instrument's exchange. This includes Exchange name, exchange code and open status.
    ExchangeInfo = "ExchangeInfo"
    # Greeks for Option(s), only applicable to Fx Options , Contract Options and Contract options CFD
    Greeks = "Greeks"
    # Individual Positions. Base data, which does not change with client/account view, or market data
    PositionBase = "PositionBase"
    # Individual PositionId only.
    PositionIdOnly = "PositionIdOnly"
    # Individual Positions. Dynamic Data, which changes with client/account view, or market data
    PositionView = "PositionView"


# Defines possible values for position or net position status.
class PositionStatus(str, Enum):
    Open = "Open"
    PartiallyClosed = "PartiallyClosed"
    Closing = "Closing"  # Closing with market order
    Closed = "Closed"
    RelatedClose = "RelatedClose"  # Related closing position
    Locked = "Locked"  # Locked by back office
    Square = "Square"  # Implicitly closed. Used for Net Positions only.


class PriceDisplayFormatType(str, Enum):
    # Display the last digit as a smaller than the rest of the numbers.
    # Note that this digit is not included in the number of decimals, effectively increasing the number of decimals by one.
    # E.g. 12.345 when Decimals is 2 and DisplayFormat is AllowDecimalPips.
    AllowDecimalPips = "AllowDecimalPips"
    # Display the last two digits as a smaller than the rest of the numbers.
    AllowTwoDecimalPips = "AllowTwoDecimalPips"
    # Decimals are denoted in as a fractions. Common for commodity futures. PriceDecimals indicated the nominator.
    Fractions = "Fractions"
    # Display as modern faction, e.g. 1’07.5.The Decimals field indicates the fraction demoninator as 1/(2^x).
    # So if Decimals is 5, the value should represent the number of 1/32'ths
    ModernFractions = "ModernFractions"
    # No special display format for this price.
    Normal = "Normal"
    # Display as percentage, e.g. 12.34%.
    Percentage = "Percentage"


# Specifies the prices to be used when returning price dependent values. Default is “RegularTradingHours”.
class PriceMode(str, Enum):
    # Price calculation is based on extended trading hours.
    ExtendedTradingHours = "ExtendedTradingHours"
    # Default price calculation mode. Price calculation is based on regular trading hours.
    RegularTradingHours = "RegularTradingHours"


class TradeLevel(str, Enum):
    FullTradingAndChat = "FullTradingAndChat"
    OrdersOnly = "OrdersOnly"


class TradingStatus(str, Enum):
    NotDefined = "NotDefined"
    # Instrument is non tradable
    NonTradable = "NonTradable"
    # Instrument is Reduce only, which means client can only reduce the exposure
    # by closing existing open position(s) and cannot open new position(s).
    ReduceOnly = "ReduceOnly"
    # Instrument is tradable
    Tradable = "Tradable"


class AccountKey(str):
    pass


class ClientKey(str):
    pass


class ContextId(str):
    MAX_ID_LENGTH: int = 50
    MIN_ID_LENGTH: int = 1
    ACCEPTABLE_CHARS: str = string.ascii_letters + string.digits + "-"

    def __new__(cls, v: Optional[object] = None) -> ContextId:
        id = v if v else str(uuid4())
        if not cls.validate(id):
            raise ValueError
        return super().__new__(cls, id)

    @classmethod
    def validate(cls, v: object) -> bool:
        chars = str(v)
        return all([c in cls.ACCEPTABLE_CHARS for c in chars]) and (
            cls.MIN_ID_LENGTH <= len(chars) <= cls.MAX_ID_LENGTH
        )


class ReferenceId(str):
    def __new__(cls, v: Optional[object] = None) -> ReferenceId:
        id = v if v else str(uuid4())
        return super().__new__(cls, id)

    @classmethod
    def validate(cls, v: object, _info):
        try:
            return cls(v)
        except Exception as ex:
            print(ex)
            raise ex


@unique
class ResponseCode(Enum):
    OK = 200
    CREATED = 201
    ACCEPTED = 202  # 202 is not documented, but returned actually.
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

    @property
    def is_successful(self) -> bool:
        return self.value < 400

    @property
    def is_error(self) -> bool:
        return 400 <= self.value


class InlineCountValue(Enum):
    """
    Defines an enumeration for $inlinecount query option values.
    """

    ALL_PAGES = (
        "AllPages"  # The results will contain a total count of items in the queried dataset.
    )
    NONE = "None"  # The results will not contain an inline count.
