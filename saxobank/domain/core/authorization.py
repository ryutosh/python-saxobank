from typing import Optional


class Token:
    def __init__(
        self, access_token: str, refresh_token: str, redirect_uri: Optional[str] = None, code_verifier: Optional[str] = None
    ):
        pass
