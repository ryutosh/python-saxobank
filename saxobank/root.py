from .models import enums as e


class SessionCapability:
    def __init__(self, _session_capability_repository: SessionCapabilityRepository):
        self._session_capability_repository = _session_capability_repository
        self._trade_level = None
        self._authentication_level = None

    def trade_level(self) -> e.TradeLevel:
        return self._trade_level

    def change_trade_level(self, _new_trade_level: e.TradeLevel) -> None:
        pass


class SessionCapabilityRepository:
    def __init__(self):
        pass

    def 
