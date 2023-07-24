# from decimal import Decimal

# import pytest
# from saxobank import models, order

# tick_size_scheme1 = models.TickSizeSchemeResponse.parse_raw(
#     """
# {
#    "DefaultTickSize": 0.01,
#    "Elements": [ { "HighPrice": 0.199,
#        "TickSize": 0.001
#      },
#      {
#        "HighPrice": 1.995,
#        "TickSize": 0.005
#      }
#    ]
# }
# """
# )


# tick_size_scheme2 = models.TickSizeSchemeResponse.parse_raw(
#     """
# {
#   "DefaultTickSize": 10,
#   "Elements": [
#     {
#       "HighPrice": 10,
#       "TickSize": 10
#     }
#   ]
# }
# """
# )


# tick_size_scheme3 = models.TickSizeSchemeResponse.parse_raw(
#     """
# {
# "DefaultTickSize": 0.01,
# "Elements": [
# {
# "HighPrice": 0.9999,
# "TickSize": 0.0001
# }
#     ]
# }
# """
# )


# @pytest.mark.parametrize(
#     "tick_size_scheme, price, expected",  # fixture names
#     [
#         (tick_size_scheme1, "0.001", "0.001"),
#         (tick_size_scheme1, "0.199", "0.001"),
#         (tick_size_scheme1, "0.2", "0.005"),
#         (tick_size_scheme1, "1.99", "0.005"),
#         (tick_size_scheme1, "2", "0.01"),
#         (tick_size_scheme1, "40", "0.01"),
#         (tick_size_scheme2, "0.01", "10"),
#         (tick_size_scheme2, "2.5", "10"),
#         (tick_size_scheme3, "0.01", "0.0001"),
#         (tick_size_scheme3, "0", "0.0001"),
#         (tick_size_scheme3, "0.9999", "0.0001"),
#         (tick_size_scheme3, "0.99999", "0.01"),
#         (tick_size_scheme3, "1", "0.01"),
#     ],
# )
# def test_tick_size_from_scheme(tick_size_scheme, price, expected):
#     calculated = order.tick_size_from_scheme(tick_size_scheme, Decimal(price))
#     assert calculated == Decimal(expected)


# @pytest.mark.parametrize(
#     "tick_size, price, expected",  # fixture names
#     [
#         ("0.001", "0.028", "0.028"),
#         ("0.001", "1.1234", "1.123"),
#         ("0.005", "1.99003", "1.990"),
#         ("0.005", "1.99803", "2.000"),
#         ("0.01", "2.87654", "2.88"),
#     ],
# )
# def test_conform_price_to_tick_size(tick_size, price, expected):
#     calculated = order.conform_price_to_tick_size(Decimal(tick_size), Decimal(price))
#     assert calculated == Decimal(expected)


# def test_ticker_amount_float_type():
#     # ref model
#     ref = models.InstrumentsDetailsResponse()

#     # float value
#     v = 1.23
#     r = order.conform_amount(ref, v)
#     assert v == r


# # def test_ticker_amount_decimal_type():
# #     # ref model
# #     ref = models.InstrumentsDetailsResponse()

# #     # decimal value
# #     f_amount = [1.2345678, 12345678.9, 0.0000, 0]
# #     d_amount = [Decimal(str(x)) for x in f_amount]
# #     r_amount = [order.conform_amount(ref, x) for x in d_amount]
# #     assert d_amount == r_amount


# def test_ticker_amount_decimal_type():
#     # ref model
#     dec = [0, 1, 2]
#     ref = [models.InstrumentsDetailsResponse(AmountDecimals=x) for x in dec]

#     # decimal value
#     f_amount = [1.2345678, 2345678.9, 0.0000, 0, -345.678]
#     d_amount = [Decimal(str(x)) for x in f_amount]
#     r_amount = [order.conform_amount(y, x) for x in d_amount for y in ref]
#     f_exp = [1, 1.2, 1.23, 2345679, 2345678.9, 2345678.90, 0, 0.0, 0.00, 0, 0.0, 0.00]
#     d_exp = [Decimal(str(x)) for x in f_exp]
#     for x, y in zip(d_exp, r_amount):
#         assert x == y


# def test_conform_price_to_format():
#     _ = models.PriceDisplayFormatResponse(OrderDecimals=1)
