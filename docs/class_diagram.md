
```mermaid
classDiagram

    class ApplicationEnvironment{
        - app_url
        - environment_mode
        - application_key
        - application_secret
        + auth_header()
        + open_api_base_url()
    }

    %% ==================== Session ==========================
    class Token{
        <<Entity>>
        - access_token
        - refresh_token
        - redirect_uri
        - code_verifier
        - ListCallable observers
        - semaphoe refreshing
        + get_token()
        + renew(str access_token)
    }
    class RateLimiter {
        <<Entity>>
        - dimension
        - remaining
        - reset_after
        + __init__(dimension, header_info)
        + __eq__(dimension)
    }
    %%class TradeLevel {
    %%    <<Enumeration>> 
    %%}
    %%TradeLevel <.. SessionCapability
    %%class SessionCapability{
    %%    trade_level
    %%    NG: change_trade_level(trade_level)
    %%}
    %%class ContextId {
    %%    <<ValueObject>>
    %%    + __init__()
    %%}
    class Subscription{
        <<Entity>>
        + reference_id
        - queue
        + __init__(reference_id, queue)
        + coroutine get()
        + coroutine put()

    }
    %%ContextId <.. StreamingSession
    Subscription <.. StreamingSession
    class StreamingSession{
        <<Entity>>
        + context_id
        + Token token
        + __init__(WebSocketClient ws_client, Token token, str context_id, str ws_base_url)
        - _on_token_refresh(str access_token)
        + connect(): Stream
        + reconnect(int message_id): Stream
        + disconnect()
        + re_authorize(str access_token)
    }
    %%RateLimit <.. SessionRateLimits
    %%class SessionRateLimits {
    %%    <<CollectionObject>>
    %%    - List<~rate_limit~>
    %%    + apply(dimension, header_info)
    %%    + throttle_time(dimension, time)
    %%}
    class OAuthClientType{
        <<Enumeration>>
    }
    class EndPoint {
        <<DataClass>>
        + str url
        + HttpMethod method
        + Dimension dimension
        + ContentType content_type
    }
    class SaxobankModel{
        <<DataClass>>
    }
    %%ContextId <.. UserSession
    Token <.. UserSession: use
    OAuthClientType <.. UserSession: use
    StreamingSession <.. UserSession
    RateLimiter <.. UserSession: use
    EndPoint <.. UserSession
    SaxobankModel <.. UserSession
    %%SessionRateLimits <.. UserSession: use
    %%SessionCapability <.. UserSession: has
    class UserSession{
        <<Entity>>
        - Token token
        - RateLimiter limiter
        %% - RateLimit application_rate_limit
        %%- session_rate_limits
        - StreamingSession streaming_session
        %%- context_association[context_id, streaming_session]
        + __init__(HttpClient http_client, Token token, RateLimiter rate_limiter, str rest_url)
        %% + coroutine code_grant(oauth_client_type, app_key, app_secret, authorization_code, redirect_uri): bool
        %% + coroutine refresh_token(oauth_client_type, app_key, app_secret): bool
        %% + coroutine create_streaming(str context_id, str ws_base_url): StreamingSession
        + coroutine subscribe(Subscription subscription, args): readable
        %% OpenAPI accesses
        + coroutine place_new_orders(SaxobankModel request, datetime effectical_until, str access_token = None): SaxobankModel
    }

    %% ==================== Auth ==========================
    OAuthClientType <.. AuthService
    UserSessions <.. AuthService
    class AuthService{
        <<ApplicationService>> 
        + __init__(self, application_environment)
        + code_grant(session_id, oauth_client_type, authorization_code, redirect_uri, code_verifier, auto_refresh_token)
        + run()
    }


```