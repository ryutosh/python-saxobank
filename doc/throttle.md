```mermaid
classDiagram

    class Token{
        - +coroutine get_token() : token_header
    }
    class RateLimit{
        - +coroutine wait(Dimension dimension)
    }
    class UserSession{
        <<Entity>>
        - session_id
        - token
        - session_capability
        - RateLimit application_rate_limit
        %%- session_rate_limits
        - streaming_session
        %%- context_association[context_id, streaming_session]
        + __init__(session_id, aiohttp_client_session, auth_url, rest_url, ws_url, application_rate_limit)
        -bool __eq__(self, UserSession)
        +coroutine code_grant(oauth_client_type, app_key, app_secret, authorization_code, redirect_uri): bool
        +coroutine refresh_token(oauth_client_type, app_key, app_secret): bool
        +coroutine subscribe(url, args): Subscription
        +coroutine request_response(dimension, url, http_method, content_type, need_token_auth, is_order)
    }

