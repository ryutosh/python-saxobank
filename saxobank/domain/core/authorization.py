from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator


class AuthorizationError(Exception):
    def __init__(self, **arg):
        self.arg = arg


class NotAuthorizedError(AuthorizationError):
    def __init__(self, **arg):
        self.arg = arg


class AuthorizationExpiredError(NotAuthorizedError):
    def __init__(self, **arg):
        self.arg = arg

    def __str__(self):
        return f"Request Error."


class OAuth2Authorization:
    """
    A token capsule that orchestrate referencing and refreshing of access token to avoid crash them same time.

    But, RFC6749 doesn't describe about life-time of old access token after new access token issued.
    https://datatracker.ietf.org/doc/html/rfc6749
    If old access token still available until its expire, this orchestration not needed.

    [Usage]
    Token consumer:
    async with oauth2_authorization.access_token() with access_token:
        request.get(url, token=access_token)

    Token refresher:
    async with oauth2_authorization.refresh_token() with refresh_token:
        response = request.post(auth_url, data={"refresh_token": refresh_token}, headers=auth_header)
        j = response.json()
        oauth2_authorization.set_tokens(j["access_token"], j["refresh_token"])
    """

    def __init__(self, access_token: str, refresh_token: str):
        # initialize primitivs
        self._token_ready = asyncio.Event()
        self._token_ready.set()
        self._num_token_using = 0
        self._token_untouched = asyncio.Event()
        self._token_untouched.set()

        # initialize authinfo
        self.set_tokens(access_token, refresh_token)

    def _mark_untouch(self) -> None:
        if self._num_token_using == 0:
            self._token_untouched.set()

    def _touch_token(self) -> None:
        self._num_token_using += 1
        self._token_untouched.clear()

    def _untouch_token(self) -> None:
        self._num_token_using -= 1
        self._mark_untouch()

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        self._access_token = access_token
        self._refresh_token = refresh_token

    @asynccontextmanager
    async def access_token(self) -> AsyncIterator[str]:
        await self._token_ready.wait()
        try:
            self._touch_token()
            yield self._access_token
        finally:
            self._untouch_token()

    @asynccontextmanager
    async def refresh_token(self) -> AsyncIterator[str]:
        self._token_ready.clear()
        await self._token_untouched.wait()
        try:
            yield self._refresh_token
        finally:
            self._token_ready.set()


def keep_refresh(auth):
    async with auth.refresh_token() as refresh_token:
        response = await self.http_client.request(endpoints.HttpMethod.POST, url, data=data, auth=auth)
        auth.set_tokens(response.access_token, response, refresh_token)
