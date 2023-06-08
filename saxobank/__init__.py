# from enum import Enum

# from winko import config

# from . import dispatcher


# class ServiceState(Enum):
#     """
#     Define saxobank trading state
#     """

#     RUNNING = 1
#     NO_ENTRY = 2
#     STOPPING = 10


# service_state = ServiceState.RUNNING

# S = config["saxobank"]
# saxobank_request_dispatcher = dispatcher.SaxobankRequestDispatcher(
#     app_mode=S.get("APP_MODE"),
#     app_key=S.get("APP_KEY"),
#     app_secret=S.get("APP_SECRET"),
#     connector_limit=16,  # Num of service groups
#     request_timeout_connect=S.get("REQUEST_TIMEOUT_CONNECT"),
#     token_refresh_threhold=0.8,
# )
