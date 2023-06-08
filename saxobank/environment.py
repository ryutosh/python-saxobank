from dataclasses import dataclass
from enum import Enum


class AuthBaseUrl(str, Enum):
    LIVE = "https://live.logonvalidation.net/"
    SIM = "https://sim.logonvalidation.net/"


class RestBaseUrl(str, Enum):
    LIVE = "https://gateway.saxobank.com/openapi/"
    SIM = "https://gateway.saxobank.com/sim/openapi/"


class WsBaseUrl(str, Enum):
    LIVE = "https://streaming.saxobank.com/openapi/streamingws/"
    SIM = "https://streaming.saxobank.com/sim/openapi/streamingws/"


@dataclass(frozen=True)
class __SaxobankEnvironmentDefinition:
    auth_base_url: AuthBaseUrl
    rest_base_url: RestBaseUrl
    ws_base_url: WsBaseUrl


# LIVE = SaxobankEnvironment(auth_base_url=AuthBaseUrl.LIVE, rest_base_url=RestBaseUrl.LIVE, ws_base_url=WsBaseUrl.LIVE)
# SIM = SaxobankEnvironment(auth_base_url=AuthBaseUrl.SIM, rest_base_url=RestBaseUrl.SIM, ws_base_url=WsBaseUrl.SIM)


class SaxobankEnvironment(__SaxobankEnvironmentDefinition, Enum):
    LIVE = __SaxobankEnvironmentDefinition(
        auth_base_url=AuthBaseUrl.LIVE, rest_base_url=RestBaseUrl.LIVE, ws_base_url=WsBaseUrl.LIVE
    )
    SIM = __SaxobankEnvironmentDefinition(
        auth_base_url=AuthBaseUrl.SIM, rest_base_url=RestBaseUrl.SIM, ws_base_url=WsBaseUrl.SIM
    )
