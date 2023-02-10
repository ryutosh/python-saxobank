from decimal import Decimal

from pydantic import ValidationError

from saxobank import models, order


def test_ticker_amount_float_type():
    # ref model
    ref = models.InstrumentsDetailsResponse()

    # float value
    v = 1.23
    r = order.conform_amount(ref, v)
    assert v == r


def test_ticker_amount_decimal_type():
    # ref model
    ref = models.InstrumentsDetailsResponse()

    # decimal value
    f_amount = [1.2345678, 12345678.9, 0.0000, 0]
    d_amount = [Decimal(str(x)) for x in f_amount]
    r_amount = [order.conform_amount(ref, x) for x in d_amount]
    assert d_amount == r_amount


def test_ticker_amount_decimal_type():
    # ref model
    dec = [0, 1, 2]
    ref = [models.InstrumentsDetailsResponse(AmountDecimals=x) for x in dec]

    # decimal value
    f_amount = [1.2345678, 2345678.9, 0.0000, 0, -345.678]
    d_amount = [Decimal(str(x)) for x in f_amount]
    r_amount = [order.conform_amount(y, x) for x in d_amount for y in ref]
    f_exp = [1, 1.2, 1.23, 2345679, 2345678.9, 2345678.90, 0, 0.0, 0.00, 0, 0.0, 0.00]
    d_exp = [Decimal(str(x)) for x in f_exp]
    for x, y in zip(d_exp, r_amount):
        assert x == y


def test_conform_price_to_format():
    _ = models.PriceDisplayFormatResponse(OrderDecimals=1)
