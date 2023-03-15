# # https://docs.python.org/ja/3/tutorial/errors.html

# # *******************************************************
# # Request Error
# # *******************************************************


# class RequestError(Exception):
#     def __init__(self, **arg):
#         self.arg = arg

#     def __str__(self):
#         return f"Request Error."


# class RequestUnauthorizedError(RequestError):
#     def __init__(self, **arg):
#         self.arg = arg

#     def __str__(self):
#         return f'Authorization information is not registered for {self.arg.get("winko_id", None)}.'


# class RequestForbiddenError(RequestError):
#     def __init__(self, **arg):
#         self.arg = arg

#     def __str__(self):
#         return f'Authorization information is not registered for {self.arg.get("winko_id", None)}.'


# class TooManyRequestsError(RequestError):
#     def __init__(self, **arg):
#         self.arg = arg

#     def __str__(self):
#         return f'Authorization information is not registered for {self.arg.get("winko_id", None)}.'
