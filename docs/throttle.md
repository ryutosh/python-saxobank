```mermaid
classDiagram

    class RateLimiter{
        + __init__(default_appday_limit: int, default_sg_limit: int)
        + coroutine wait(Dimension dimension)
        + coroutine consume(Dimension dimension, effectical_until datetime)
        + apply_rate_limit(tuple_or_header)
        + classmethod parse_ratelimit_header(header) -> tuple
    }
