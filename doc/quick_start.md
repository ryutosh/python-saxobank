```python
import saxobank
from saxobank.dto import AssetType, OrderAmountType, req

environment = {
    'mode': 'SIM',
    'grant_type': 'code'
    'application_key': 'XXXX',
    'application_secret': 'YYYY'
}

# Set Saxobank application
app = saxobank.Application(environment)

```

# Token
```python
# Token auth
token = await app.code_grant(auth_code, redirect_uri)
# Or you can recreate from persistence
token = app.Token(access_token=access_token, refresh_token=refresh_token, token_exp='2024-05-12T12:34:56.0000')

# If you prelong token automatically
auth_service = await AuthService(ClientType.CODE, environment.app_key, environment.app_secret, auth_url)
asyncio.create_task(auth_service.run(asyncio.get_event_loop()))
auth_service.prelong_token(token)
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