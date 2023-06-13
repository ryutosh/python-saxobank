# Goal
This library provides SaxoBank's Open API's "THIN" wrapper.
You can access your Saxobank account easily.
The library inplements SaxoBank's Open API's core business and you don't have to care bout it.

# What it NOT provides
Taking trading business manner is not the library's GOAL.
What 'market order' meant differents by users.
That's mean, the library require you to learn principals of Saxobank Open API,
but don't restrict your trading.
However the library stays thin, but also provides common functions like ticker size be regulation;
because these are common business.


# When you control authorization yourself
```python
from saxobank.application import Application
from saxobank.environment import SaxobankEnvironment
from saxobank.model.common import AssetType
from saxobank import model

# Setup application countering to Saxo OpenAPI simulation environment
saxo = Application(SaxobankEnvironment.SIM)

# Create a sesion instance to requests OpenAPI
session = saxo.create_session(access_token=your_access_token)

# Get Microsoft stock price
req = model.chart.charts.Get(AssetType=AssetType.Stock, Uic=4912, Horizon=480)
res = await session.chart_charts_get(req)
print(res.model.Data)

# Create a streaming session for realtime trade
streaming_session = session.create_streaming_session()

# Run your golden cross strategy
TARGET_ASSET={'AssetType':AssetType.FxSwap, 'Uic':99}

async def market_order(buy_sell):
    req = model.trade.order.Post(**TARGET_ASSET, BuySell=buy_sell, Amount=1)
    res = await session.trade_order_post(req)

    if res.code.is_success():
        print(f'Ordered!')

async def subscribe_chart(resolution, old_ref_id = None):
    arg = models.trade.ChartSubscriptionReq(**TARGET_ASSET, Resolution=resolution)
    subscription = await streaming.chart_charts_subscription_post(arguments=arg, replace_reference_id=old_ref_id)
    return subscription.model.ReferenceId

async def your_strategy(stream):
    ref_short = await subscribe_chart(60)
    ref_long = await subscribe_chart(480)

    while True:
        try:
            short = await stream.receive(ref_short):

            if something:
                buy()

        except ResetSubscriptionException as ex:
            if ex.reference_id == ref_short:
                ref_short = await subscribe_chart(60)


async with streaming_session.connect(access_token=your_access_token) as stream:
    await your_strategy(stream)

# or
stream = streaming_session.connect(access_token=your_access_token)
await your_strategy(stream)
#await streaming_session.disconnect()
await stream.disconnect()

# or
stream = streaming_session.connect(access_token=your_access_token)
async with stream:
    await your_strategy(stream)


# async with streaming.connect() as stream:

#     snapshot = res.snapshot
#     queue.put(snapshot)

#     async for data in stream:
#         if data.reference_id == chart_subscription.reference_id:
#             snapshot.accept_delta(data.payload)
#             queue.put(snapshot)
        
#         elif data.reference_id == '_reset_subscription':
#             chart_subscription.remove()
#             res = await chart_subscription.create(arguments=req_chart, format=models.Format.Json, refresh_rate=1, tag="strategy1")
        
#         elif data.reference_id == '_heartbeat' and data.reason == 'PermanentlyDisabled':
#             queue.put(PermanentlyDisabledException())
#             break

#         elif data.reference_id == '_disconnect':
#             queue.put(DisconnectException())
#             alert()
#             break

await streaming.chart_delete_multiple_subscriptions(tag="strategy1")




# Tell new access token if changed
await streaming.re_auth(access_token='yyyy')


# Utils
# Task whatch your session capability and stay FullTrade 
# asyncio.create_task(saxo.keep_session_capability())



```
# Use with auto trading
Since access token has short life-time, might be expired while your auto-trading application running.
That will make your application unavailable to communicate with Saxobank then trade can't be continue.
Thus, the package provides an utility service that automatically renews access token using refresh token.
Remind that refresh token has longer life-time than access token, but also expires in someday.
If this happen, token will not renewed. Don't forget to stop auto-trading before you into Mt.Everest.

```python
# User Sesion
session = saxo.create_session(sqlib='abc.dat', access_token='abcde')
asyncio.create_task(your_strategy(session))

# Prelong service
srv = saxo.PrelongTokenService()
try:
    asyncio.run_until_complete(srv.keep_refresh(refresh_token, on_success=[session.set_token]))
except TokenRefreshError as err:
    call_you(err)

```

# Set RateLimit
```python
app_rate_limit = saxobank.RateLimit(dimension='app', 1000000)
session_rate_limit = saxobank.RateLimit(dimension='app', 1000000)
```

# Create Session to access OpenAPI
```python
user_session = saxobank.UserSession(token, rate_limitter, rest_base_url='https://abc', ws_base_url='ws://abc')
```

# OpenAPI access
```python
req_orders = req.Orders(
    Amount=10.0,
    AmountType=OrderAmountType.CurrencyAmount
    )
res_orders = await user_session.place_new_order(req_orders)

# Or, you can control token yourself
res_orders = await user_session.place_new_order(req_orders, access_token=access_token)

# Ummm...
async with auth.auth_header() as auth_header:
    res_orders = await user_session.place_new_order(req_orders, auth_header)


```

# Streaming
```python
context_id=100
reference_id=['chart1', 'chart2', 'chart3']
req_chart = req.ChartSubscriptionRequest(
    AssetType=AssetType.FxSwap,
    Uic=99
)


# Create streaming
streaming = user_session.create_streaming()
listner = await streaming.connect(context_id=context_id)
# or
streaming = saxobank.StreamingSession(user_session=user_session)
listner = await streaming.connect(context_id=context_id)

# Start subscription
await user_session.create_chart_subscription(context_id=context_id, reference_id=reference_id, arguments=req_chart)
# or
await streaming.create_chart_subscription(reference_id=reference_id, arguments=req_chart)

# you can recreate from persistence
listner = await streaming.reconnect(context_id=context_id, last_message_id=10)

# Ends-up subscription
await user_session.remove_chart_subscription(context_id=context_id, reference_id=reference_id[0])
await streaming.disconnect()
# or
await streaming.remove_chart_subscription(reference_id=reference_id[0])
await streaming.disconnect()
```