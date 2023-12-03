# # https://docs.python.org/ja/3/tutorial/errors.html
from typing import Set

from .model.common import ReferenceId


class SaxoException(Exception):
    pass
    # def __init__(self, *args, **kwargs) -> None:
    #     super().__init__(*args, **kwargs)


class StreamingError(SaxoException):
    pass


class ResetSubscriptionsError(StreamingError):
    def __init__(self, reference_ids: Set[ReferenceId]) -> None:
        self.reference_ids = reference_ids

    def __str__(self) -> str:
        return f"Subscription of Reference ID {self.reference_ids} need to delete and re-create."


class SubscriptionTimeoutError(StreamingError):
    def __init__(self, reference_ids: Set[ReferenceId]) -> None:
        self.reference_ids = reference_ids

    def __str__(self) -> str:
        return f"Subscription of Reference ID {self.reference_ids} timed out."


class SubscriptionPermanentlyDisabledError(StreamingError):
    def __init__(self, reference_ids: Set[ReferenceId]) -> None:
        self.reference_ids = reference_ids

    def __str__(self) -> str:
        return f"Subscription of Reference ID {self.reference_ids} will be unavailable."


class StreamingDisconnectError(StreamingError):
    def __str__(self) -> str:
        return f"Stream was disconnected. Client may reset password. Need to authorize again and recreate subscriptions."


class RequestError(SaxoException):
    pass


class NoAccessTokenError(RequestError):
    pass


class HttpClientError(RequestError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"HttpClient raised an error. {self.message}"


# class RequestUnauthorizedError(RequestError):
#     def __str__(self):
#         return f"Unauthorized."


# class RequestForbiddenError(RequestError):
#     def __str__(self):
#         return f"Forbidden."


# class RequestNotFoundError(RequestError):
#     def __str__(self):
#         return f"Not Found."


# class TooManyRequestsError(RequestError):
#     def __str__(self):
#         return f"Too many requests. Quotas are exceeded."


# class SaxobankServiceError(RequestError):
#     def __str__(self):
#         return f"Saxo OpenAPI raised internal service error."


# class SaxobankServiceUnavailableError(RequestError):
#     def __str__(self):
#         return f"Saxo OpenAPI raised service unavailable error."


class ResponseError(SaxoException):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message

    def __str__(self) -> str:
        return f"Exception happend after getting response from server with status code {self.status}. {self.message}"


class InternalError(SaxoException):
    def __init__(self, debug_message: str):
        self.debug_message = debug_message

    def __str__(self) -> str:
        return f"Internal Error. {self.debug_message}"


# class RequestError(Exception):
#     def __init__(self, **arg):
#         self.arg = arg

#     def __str__(self):
#         return f"Request Error."
