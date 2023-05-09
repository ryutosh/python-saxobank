import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import aiohttp
import simplejson as json
from multidict import CIMultiDictProxy
from winko import exceptions

from . import endpoints

logger = logging.getLogger(__name__)


@dataclass
class OAuthInfo:
    import datetime

    auth_code = None
    redirect_uri = None
    access_token = None
    refresh_token = None
    refreshed_at = None

    def set_tokens(self, access_token, refresh_token, refreshed_at):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.refreshed_at = refreshed_at


CONTENT_TYPE_JSON = "application/json"


def _headers_info(dimension: str, headers: CIMultiDictProxy):
    logger.debug(f"THRT: headers containing X-RateLimit are..")
    for k, v in filter(lambda x: "X-RateLimit" in x[0], headers.items()):
        logger.debug(f"THRT: {k:_<46} -> {v}")

    if (limit := headers.get(f"X-RateLimit-{dimension}-Limit", None)) is not None:
        limit = int(limit)

    if (remaining := headers.get(f"X-RateLimit-{dimension}-Remaining", None)) is not None:
        remaining = int(remaining)

    if (reset := headers.get(f"X-RateLimit-{dimension}-Reset", None)) is not None:
        reset = int(reset)

    return limit, remaining, reset


class Throttle:
    def __init__(self, is_order: bool = False):
        self.is_order = is_order

        # Rate-limit initialize
        self.limit = 1 if is_order else 120
        self.remaining = None
        self.reset_interval = 1 if is_order else 60
        self.reset_after = None

    def consume(self, limit=None, remaining=None, reset=None):
        # Update limit info
        if limit is not None:
            self.limit = limit

        # Update remaining
        self.remaining = (
            remaining if remaining is not None else (self.remaining if self.remaining is not None else self.limit) - 1
        )

        # Update reset after
        self.reset_after = datetime.now(timezone.utc) + timedelta(
            seconds=max(reset if reset is not None else self.reset_interval, 1)
        )
        logger.debug(f"THRT: Consumed. Remaining:{self.remaining}, ResetAfter: {str(self.reset_after)}")

    def _throttle_time(self):
        now = datetime.now(timezone.utc)

        # If not consumed yet, don't need to throttle.
        if self.remaining is None or self.reset_after is None:
            return 0, now

        # Throttle time
        sec_waits = (self.reset_after - now).total_seconds() if self.remaining <= 0 else 0
        estimated = now + timedelta(seconds=sec_waits)

        logger.debug(f"THRT: Wait Seconds:{sec_waits} and estimated time: {str(estimated)}")
        return sec_waits, estimated

    async def throttle(self, effectual_until=None):
        sec_waits, estimated_time = self._throttle_time()

        # If estimated time overs effectual until time, raise exp.
        if effectual_until and (effectual_until < estimated_time):
            raise exceptions.DispatchUntilError(requested=effectual_until, estimated=estimated_time)

        # Throttle sec_waits
        if 0 < sec_waits:
            await asyncio.sleep(sec_waits)
            await self.throttle(effectual_until)


class StackedEvent:
    def __init__(self):
        self.count = 0
        self.event = asyncio.Event()
        self._init_event()

    def _init_event(self):
        if self.count == 0:
            self.event.set()

    async def wait(self):
        await self.event.wait()

    def append(self):
        self.count = self.count + 1
        self.event.clear()

    def pop(self):
        self.count = self.count - 1
        self._init_event()


class SaxobankUserSession:
    def __init__(
        self,
        app_mode,
        app_key,
        app_secret,
        connector_limit,
        request_timeout_connect,
        token_refresh_threhold,
    ):
        if app_mode == "LIVE":
            self.rest_gateway = endpoints.GATEWAY_LIVE
            self.url_authorize = "https://live.logonvalidation.net/authorize"
            self.url_token = "https://live.logonvalidation.net/token"
        elif app_mode == "SIM":
            self.rest_gateway = endpoints.GATEWAY_SIM
            self.url_authorize = "https://sim.logonvalidation.net/authorize"
            self.url_token = "https://sim.logonvalidation.net/token"

        self.app_key = app_key
        self.app_secret = app_secret

        # Endpoint access controls
        self.services_requesting_flags = {}  # Serialize endpoint requests per service groups(rate limit dimensions)
        self.throttles = {}  # Throttle objects for each rate limit dimensions

        # Token access controls
        self.token_refresh_threhold = token_refresh_threhold
        self.authinfo = None
        self.token_refreshing = asyncio.Event()
        self.token_refreshing.set()
        self.token_refresh_task = None
        self.token_accesses = StackedEvent()  # Requests using  token

        # The session contains a cookie storage and connection pool,
        # thus cookies and connections are shared between HTTP requests sent by the same session.
        connector = aiohttp.TCPConnector(limit=connector_limit)
        timeout = aiohttp.ClientTimeout(connect=request_timeout_connect)
        self.http_session = aiohttp.ClientSession(connector=connector, timeout=timeout, json_serialize=json.dumps)

        logger.info("New user session created.")

    def __del__(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self.http_session.close())
        else:
            loop.create_task(self.http_session.close())

    def auth_url(self, redirect_uri, state_string=None):
        if not self.authinfo:
            self.authinfo = OAuthInfo()

        self.authinfo.redirect_uri = redirect_uri

        req_params = {
            "response_type": "code",
            "client_id": self.app_key,
            "redirect_uri": redirect_uri,
        }
        if state_string:
            req_params["state"] = state_string

        return self.url_authorize + "?" + urlencode(req_params)

    def add_authinfo(self, auth_code):
        if not self.authinfo:
            self.authinfo = OAuthInfo()
        self.authinfo.auth_code = auth_code

        self.token_refresh_task = asyncio.create_task(self.refresh_token())

    def remove_authinfo(self):
        if self.token_refresh_task:
            self.token_refresh_task.cancel()
        self.authinfo = None

    def _get_auth_header(self):
        # Caution: Difference between schemes
        #  OAuth:client_id      Saxo:AppKey     ex.1234-5678-9101
        #  OAuth:client_secret  Saxo:AppSecret  ex.abcdefghijklmn
        return aiohttp.BasicAuth(self.app_key, password=self.app_secret)

    def _get_bearer_header(self):
        if not self.authinfo or not self.authinfo.access_token:
            raise exceptions.AuthorizationNotRegisteredError()

        return {"Authorization": f"Bearer {self.authinfo.access_token}"}

    def _token_req_body(self):
        return (
            {
                "grant_type": "refresh_token",
                "refresh_token": self.authinfo.refresh_token,
                "redirect_uri": self.authinfo.redirect_uri,
            }
            if self.authinfo.refresh_token
            else {
                "grant_type": "authorization_code",
                "code": self.authinfo.auth_code,
                "redirect_uri": self.authinfo.redirect_uri,
            }
        )

    async def refresh_token(self, wait=0):
        logger.debug(f"TOKN: Refresh will start after wait: {wait}")
        await asyncio.sleep(wait)

        self.token_refreshing.clear()
        await self.token_accesses.wait()

        try:
            status, headers, body = await self.request_http(
                endpoints.HttpMethod.POST, self.url_token, data=self._token_req_body(), account_auth=True
            )

        except exceptions.RequestError as ex:
            logger.error(f"TOKN: Refresh request got error, then not continue next refresh: {ex}")

        else:
            if status < 400:
                logger.debug("TOKN: Refresh succeed.")
                self.authinfo.set_tokens(body["access_token"], body["refresh_token"], datetime.now(timezone.utc))

                standby_time = timedelta(seconds=body["expires_in"]) * self.token_refresh_threhold
                self.token_refresh_task = asyncio.create_task(self.refresh_token(standby_time.total_seconds()))

            else:
                logger.error(f"TOKN: Refresh request was not ok with status {status}, then not continue next refresh.")

        finally:
            self.token_refreshing.set()

    def _raise_if_timeup(self, effectual_until, estimated_time):
        if effectual_until and (effectual_until < estimated_time):
            raise exceptions.DispatchUntilError(requested=effectual_until, estimated=estimated_time)

    async def request_http(
        self,
        method: str,
        url: str,
        params=None,
        data=None,
        json_data=None,
        account_auth: bool = False,
        token_auth: bool = False,
        effectual_until=None,
    ):

        # Wait token refreshing if use it
        if token_auth:
            await self.token_refreshing.wait()

        self._raise_if_timeup(effectual_until, datetime.now(timezone.utc))

        # token access
        if token_auth:
            self.token_accesses.append()

        # Set authorization header with username and password if needed
        auth = self._get_auth_header() if account_auth else None

        # Set authorization header with a bearer token if needed
        headers = self._get_bearer_header() if token_auth else None

        try:
            logger.debug(f"HTTP: Requesting to URL: {url}")
            response = await self.http_session.request(
                method, url, params=params, data=data, json=json_data, headers=headers, auth=auth
            )

        except aiohttp.ClientResponseError as ex:
            logger.error(f"HTTP: Request failed with ClientError: {ex}")
            raise exceptions.ResponseError(ex.request_info, ex.status, ex.headers)

        except aiohttp.ClientError as ex:
            logger.error(f"HTTP: Request failed with ClientError: {ex}")
            raise exceptions.RequestError()

        else:
            async with response:
                status = response.status
                headers = response.headers
                body = await response.json() if response.content_type == CONTENT_TYPE_JSON else None
                request_info = response.request_info

            logger.debug(f"HTTP: Response returned with status:{status}.")

        finally:
            if token_auth:
                self.token_accesses.pop()

        if 401 <= status:
            logger.error(f"HTTP: Req info: {request_info}")
            logger.error(f"HTTP: Res body: {body}")
            raise exceptions.ResponseError(request_info, status, headers)

        return status, headers, body

    async def request_endpoint(self, endpoint, data=None, path_conv=None, effectual_until=None):
        logger.info(f"REQ : Requesting Endpoint: [{endpoint.method}] {endpoint.url}")

        # 非同期で処理している都合上、リクエストに対するレスポンスが発行順に届くとは限らない。
        # そのため、最後に届いたレスポンスヘッダのリミット情報が必ずしも最新の情報ではない可能性もある。
        # 最新の情報が必ず最後に届くように、リクエスト発行からレスポンス取得までをロックで制御する。
        requesting_flag = self.services_requesting_flags.setdefault(endpoint.ratelimit_dimension, asyncio.Lock())
        await requesting_flag.acquire()

        # Request as http
        headers = None
        try:
            # Throttle if Rate-limit dimension
            if endpoint.ratelimit_dimension:
                await self.throttles.setdefault(endpoint.ratelimit_dimension, Throttle(endpoint.is_order)).throttle(
                    effectual_until
                )

            status, headers, body = await self.request_http(
                endpoint.method,
                self.rest_gateway + (endpoint.url.format(**path_conv) if path_conv else endpoint.url),
                params=data if endpoint.method == endpoints.HttpMethod.GET else None,
                data=data
                if endpoint.method != endpoints.HttpMethod.GET and endpoint.req_content != endpoints.ContentType.JSON
                else None,
                json_data=data
                if endpoint.method != endpoints.HttpMethod.GET and endpoint.req_content == endpoints.ContentType.JSON
                else None,
                account_auth=False if endpoint.token_auth else True,
                token_auth=True if endpoint.token_auth else False,
                effectual_until=effectual_until,
            )

        finally:
            # Consume rate-limit
            if endpoint.ratelimit_dimension:
                headers_info = _headers_info(endpoint.ratelimit_dimension, headers) if headers else (None, None, None)
                self.throttles[endpoint.ratelimit_dimension].consume(*headers_info)

            # Release requesting flag
            requesting_flag.release()

        return status, body


class SaxobankRequestDispatcher:
    def __init__(
        self,
        app_mode,
        app_key,
        app_secret,
        connector_limit,
        request_timeout_connect,
        token_refresh_threhold,
    ):
        self.app_mode = app_mode
        self.app_key = app_key
        self.app_secret = app_secret

        self.connector_limit = connector_limit
        self.request_timeout_connect = request_timeout_connect
        self.token_refresh_threhold = token_refresh_threhold
        self.users_sessions = {}

    def _user_session(self, account_identifier) -> SaxobankUserSession:
        if account_identifier not in self.users_sessions:
            self.users_sessions[account_identifier] = SaxobankUserSession(
                self.app_mode,
                self.app_key,
                self.app_secret,
                self.connector_limit,
                self.request_timeout_connect,
                self.token_refresh_threhold,
            )
        return self.users_sessions[account_identifier]

    def add_authinfo(self, account_identifier, auth_code):
        self._user_session(account_identifier).add_authinfo(auth_code)

    def auth_url(self, account_identifier, redirect_uri, state_string=None):
        us = self._user_session(account_identifier)
        return us.auth_url(redirect_uri, state_string)

    def remove_authinfo(self, account_identifier):
        self._user_session(account_identifier).remove_authinfo()
        del self.users_sessions[account_identifier]

    async def request_endpoint(self, account_identifier, endpoint, data=None, path_conv=None, effectual_until=None):
        return await self._user_session(account_identifier).request_endpoint(
            endpoint, data=data, path_conv=path_conv, effectual_until=effectual_until
        )
