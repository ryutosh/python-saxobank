from dataclasses import dataclass
from enum import Enum


class RestBaseUrl(str, Enum):
    LIVE = "https://gateway.saxobank.com/openapi/"
    SIM = "https://gateway.saxobank.com/sim/openapi/"


class WsBaseUrl(str, Enum):
    LIVE = "https://streaming.saxobank.com/openapi/streamingws/"
    SIM = "https://streaming.saxobank.com/sim/openapi/streamingws/"


class AuthBaseUrl(str, Enum):
    LIVE = "https://live.logonvalidation.net/"
    SIM = "https://sim.logonvalidation.net/"


@dataclass
class SaxobankEnvironmentDefinition:
    auth_base_url: AuthBaseUrl
    rest_base_url: RestBaseUrl
    ws_base_url: WsBaseUrl


class SaxobankEnvironment(SaxobankEnvironmentDefinition, Enum):
    LIVE = SaxobankEnvironmentDefinition(AuthBaseUrl.LIVE, RestBaseUrl.LIVE, WsBaseUrl.LIVE)
    SIM = SaxobankEnvironmentDefinition(AuthBaseUrl.SIM, RestBaseUrl.SIM, WsBaseUrl.SIM)
