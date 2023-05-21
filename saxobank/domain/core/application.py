from __future__ import annotations

from environment import Environment


class Application:
    def __init__(self, environment: Environment):
        self.env = environment

    def create_session(self, sqlite: str | None = None) -> SessionFacade:
        pass


class SessionFacade:
    def __init__(self, sqlite: str | None = None) -> None:
        pass


    async def place_new_order()