# import asyncio
# from datetime import datetime, timedelta, timezone
# from decimal import Decimal as D
# from os import path
# from pathlib import Path

# import pytest

# from saxobank import order  # , saxobank_request_dispatcher
# from saxobank import models
# from saxobank import request as saxo_req
# from saxobank.dispatcher import SaxobankUserSession


# # =======================================================
# # monkey patches
# # =======================================================
# def patched_header(_):
#     BASE_DIR = Path(__file__).resolve().parent
#     TOKEN = path.join(BASE_DIR, "24hrs.token")

#     # 24hrs token
#     # https://www.developer.saxo/openapi/token/current
#     with open(TOKEN, encoding="utf-8") as f:
#         token = f.read()
#     return {"Authorization": f"Bearer {token}"}


# Buy = models.BuySell.Buy
# Sell = models.BuySell.Sell
# ASSET_TYPE = "CfdOnIndex"
# UIC = 4912


# async def current_price():
#     # monkeypatch.setattr(SaxobankUserSession, "_get_bearer_header", patched_header)
#     infoprices_req = models.InfoPricesRequest(
#         AssetType=ASSET_TYPE, Uic=UIC, FieldGroups=[models.InfoPriceGroupSpec.PriceInfo]
#     ).dict(exclude_unset=True)

#     # Send infoprice request
#     _, infoprices_res = await saxo_req.infoprices(1, infoprices_req)
#     # _, infoprices_res = asyncio.run(saxo_req.infoprices(1, infoprices_req))
#     return infoprices_res.PriceInfo.High, infoprices_res.PriceInfo.Low


# @pytest.fixture(scope="function")
# async def keys(monkeypatch):
#     monkeypatch.setattr(SaxobankUserSession, "_get_bearer_header", patched_header)
#     _, clients_res = await saxo_req.clients_me(1, effectual_until=None)

#     return clients_res.ClientKey, clients_res.DefaultAccountKey


# async def order_market(buy_sell, quantity, take_profit=None, stop_loss=None):
#     ret = await order.market(1, ASSET_TYPE, UIC, buy_sell, quantity)

#     return ret.order_id


# @pytest.mark.parametrize(
#     ("buy_sell", "quantity", "take_profit", "stop_loss"),
#     [
#         (Buy, D("0.5"), None, None),
#         # (Sell, D("0.5"), None, D("0.9")),
#     ],
# )
# def test_market_order2(buy_sell, quantity, take_profit, stop_loss, monkeypatch):
#     # def test_market_order2(buy_sell, quantity, take_profit, stop_loss, current_price, monkeypatch):
#     monkeypatch.setattr(SaxobankUserSession, "_get_bearer_header", patched_header)

#     # price info
#     high, low = asyncio.run(current_price())

#     # place order
#     take_profit = take_profit * high if take_profit else None
#     stop_loss = stop_loss * low if stop_loss else None

#     order_id = asyncio.run(order_market(buy_sell, quantity, take_profit, stop_loss))
#     assert order_id
