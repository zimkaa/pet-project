import os
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from datetime import UTC
from datetime import datetime
from http.cookies import SimpleCookie
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

import aiohttp
from fastapi import status
from loguru import logger

from src.config.config import settings
from src.config.consts.url import URL
from src.config.consts.url import URL_GAME
from src.config.consts.url import URL_MAIN
from .telegram import send_telegram


if TYPE_CHECKING:
    import requests


LOGIN_TEXT = r'show_warn("Введите Ваш логин и пароль.",'

RELOGIN_TEXT = r"кнопку для очистки кэша Вашего браузера"

current_dir_path = Path(__file__).parent.resolve()
# COOKIE_FOLDER = os.path.join(current_dir_path, "cookies")  # noqa: ERA001
COOKIE_FOLDER = current_dir_path / "cookies"
# COOKIE_FILE_PATH = os.path.join(COOKIE_FOLDER, "cookie")  # noqa: ERA001
COOKIE_FILE_PATH = COOKIE_FOLDER / "cookie"


# logging.basicConfig(
#     level=logging.DEBUG,  # noqa: ERA001
#     handlers=[RotatingFileHandler("request.log", maxBytes=5_242_880, backupCount=10)],  # noqa: ERA001
#     format="%(asctime)s:%(levelname)s:%(filename)s:%(message)s",  # noqa: ERA001
# )  # noqa: ERA001, RUF100
# standard_logger = logging.getLogger("request_to_nl")  # noqa: ERA001

# # standard_logger.setLevel(logging.DEBUG)  # noqa: ERA001
# # handler=[RotatingFileHandler("request.log", maxBytes=5_242_880, backupCount=10)]  # noqa: ERA001
# # standard_logger.addHandler(handler)  # noqa: ERA001

# logging.getLogger("urllib3").setLevel("WARNING")  # noqa: ERA001

# for key in logging.Logger.manager.loggerDict:
#     standard_logger.debug(f"{key=}")  # noqa: ERA001


class BaseConnection(ABC):
    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def reconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_html(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def post_html(self) -> None:
        raise NotImplementedError


class Connection:
    def __init__(self, proxy: bool = False, login: str | None = None, password: str | None = None) -> None:  # noqa: FBT002, FBT001
        self.result: requests.models.Response | None = None
        self.proxy = proxy
        self._data: aiohttp.FormData | None = None
        if login and password:
            form_data = aiohttp.FormData(charset="windows-1251")
            form_data.add_field("player_nick", login)
            form_data.add_field("player_password", password)
            self._data = form_data

        self._cookies = defaultdict(SimpleCookie)
        self.login = login

        self._session: aiohttp.ClientSession

    async def start(self) -> None:
        logger.success("\n\nstart\n\n")
        self._set_session()
        await self._log_in()

    async def reconnect(self) -> None:
        await self._log_in()

    def _set_session(self) -> None:
        """Set session."""
        self._session = aiohttp.ClientSession(trust_env=self.proxy, headers=settings.connection.HEADER)

    async def close(self) -> None:
        await self._session.close()

    def _is_valid_cookies(self) -> bool:
        logger.info("_is_valid_cookies?")
        if not os.listdir(COOKIE_FOLDER):
            logger.error(f"NO FILE {COOKIE_FOLDER=}")
            return False

        # dt = datetime.now()  # noqa: ERA001
        dt = datetime.now(tz=UTC)
        dt_without_microseconds = dt.replace(microsecond=0)
        # with open(COOKIE_FILE_PATH, "rb") as file:
        #     self._cookies = pickle.load(file)  # noqa: ERA001

        # with open("./nl_cookies.txt", "r") as f:
        #     info = f.read()  # noqa: ERA001

        info = settings.person.COOKIE
        logger.debug(f"{info=}")
        self._cookies[("neverlands.ru", "/")] = SimpleCookie(info)

        logger.debug(f"COOKIES {self._cookies=}")
        if not self._cookies.get(("neverlands.ru", "/")).get("NeverExpi"):
            logger.error(f"NO COOKIES {self._cookies=}")
            return False
        timestamp = self._cookies.get(("neverlands.ru", "/")).get("NeverExpi").value
        # user = self._cookies.get(("neverlands.ru", "/")).get("NeverUser").value  # noqa: ERA001
        user = self._cookies.get(("neverlands.ru", "/")).get("NeverNick").value
        # logger.debug(f"{user=}")  # noqa: ERA001
        login = quote_plus(self.login, encoding="cp1251")
        login = login.replace("~", "%7E")
        # logger.debug(f"{login=}")  # noqa: ERA001
        if user != login:
            logger.error(f"Cookie another person {user=} != {login=}")
            return False
        if int(dt_without_microseconds.timestamp()) >= int(timestamp):
            logger.error("int(dt_without_microseconds.timestamp()) >= int(timestamp)")
            logger.error(f"{int(dt_without_microseconds.timestamp()) >= int(timestamp)}")
            logger.error(f"{int(dt_without_microseconds.timestamp())=} {int(timestamp)=}")
            return False
        return True

    def _is_logged_in(self, result: str) -> bool:
        if LOGIN_TEXT in result:
            logger.error("NOT LOGGED")
            # logger.error(f"{result=}")  # noqa: ERA001
            self._session.cookie_jar.clear()
            return False
        if RELOGIN_TEXT in result:
            logger.error("NEED RELOGIN")
            # logger.error(f"{result=}")  # noqa: ERA001
            self._session.cookie_jar.clear()
            return False
        return True

    def _save_cookies(self) -> None:
        self._session.cookie_jar.save(COOKIE_FILE_PATH)
        # # HACK: for see cookies  # noqa: FIX004
        # for cookie in self._session.cookie_jar:
        #     logger.success(f"{cookie.key} {cookie.value}")  # noqa: ERA001
        logger.success("SAVE COOKIES")

    async def _get_login(self) -> str:
        logger.info("LOGIN")

        await self.get_html(URL)
        if self._data:
            await self.post_html(URL_GAME, self._data, auth=True)
        else:
            text = f"No login data {self._data=}"
            logger.error(text)
            raise Exception(text)  # noqa: TRY002
        self._save_cookies()
        return await self.get_html(URL_MAIN)

    async def _log_in(self) -> None:
        if self._is_valid_cookies():
            self._session.cookie_jar.update_cookies(self._cookies.get(("neverlands.ru", "/")))
            logger.success("Valid cookies update_cookies")
            result = await self.get_html(URL_MAIN)
        else:
            logger.success("Log in NOT Valid cookies")
            result = await self._get_login()

        if not self._is_logged_in(result):
            # await self._get_login()  # noqa: ERA001
            msg = "LOGIN ERROR"
            raise Exception(msg)  # noqa: TRY002

        answer = await self.get_html("http://www.neverlands.ru/ch.php?lo=1&")
        logger.success(f"{answer=}")

        # self._session.cookie_jar.clear()  # noqa: ERA001
        # if self._is_valid_cookies():
        #     self._session.cookie_jar.update_cookies(self._cookies.get(("neverlands.ru", "/")))  # noqa: ERA001
        #     logger.success("Updated cookies")  # noqa: ERA001
        # await self.get_html(URL_MAIN)  # noqa: ERA001

    async def get_html(self, site_url: str, data: dict | None = None) -> str:
        call_num = 0

        async def _retry(data: dict | None = None) -> str:
            nonlocal call_num
            call_num += 1
            # standard_logger.debug(f"get_html {self.login} request send {call_num=} times {data=} {site_url=}")  # noqa: ERA001, E501
            if call_num >= 3:  # noqa: PLR2004
                self.result.headers.get("Content-Type")
                # standard_logger.error(f"get_html {self.login} call_num >= 3 {call_num=} {content=}")  # noqa: ERA001
                text = f"{self.login}----get_html--error code: {self.result.status}"
                logger.error(f"{text=}")
                send_telegram(text)
                raise Exception(text)  # noqa: TRY002

            answer = await self._session.get(site_url, params=data)  # OLD WORK
            answer.headers.get("Content-Type")
            if answer.status == status.HTTP_200_OK:
                return await answer.text()
            elif answer.status == status.HTTP_502_BAD_GATEWAY:  # noqa: RET505
                text = f"{self.login} Error get_html {answer.status}"
                send_telegram(text)
                logger.error(f"GET query 502 {text=} and {data=} and {site_url=}")
                # standard_logger.warning(f"GET query 502 {text=} and {data=} and {site_url=}")  # noqa: ERA001
                # standard_logger.error(f"{self.login} get_html {call_num=} {content=}")  # noqa: ERA001
                if call_num == 1:
                    return await _retry(data)
                raise Exception(text)  # noqa: TRY002
            elif answer.status == 546:  # noqa: PLR2004
                # standard_logger.debug(f"{site_url=}")  # noqa: ERA001
                text = f"Code NOT stopped!!! get_htmlError {answer.status} chat error DO NOTHING!"
                # standard_logger.error(text)  # noqa: ERA001
                raise Exception(text)  # noqa: TRY002
            else:
                text = f"{self.login} ---get_html--error code: {answer.status}"
                send_telegram(text)
                # standard_logger.error(
                #     f"{self.login} get_html something new code:{answer.status} {call_num=} {content=}"  # noqa: ERA001
                # )  # noqa: ERA001, RUF100
                raise Exception(text)  # noqa: TRY002

        try:
            return await _retry(data)
        except Exception as error:  # noqa: BLE001
            # request_log_text = f"{self.login}\n{self.result.status=}\n"  # noqa: ERA001
            # request_log_text += f"{site_url=}\n"  # noqa: ERA001
            # request_log_text += f"{type(data)} {data=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.text=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.content=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.headers=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.reason=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.request.body=}\n"  # noqa: ERA001
            # standard_logger.warning(request_log_text)  # noqa: ERA001
            text = f"{self.login} get_html {error=}"
            logger.error(text)
            # send_telegram(text)  # noqa: ERA001
            raise Exception(text)  # noqa: TRY002, B904

    async def post_html(self, site_url: str, data: dict | None = None, auth: bool = False) -> str:  # noqa: FBT001, FBT002
        call_num = 0

        async def _retry(data: dict | None = None) -> str:
            nonlocal call_num
            call_num += 1
            # standard_logger.debug(f"{self.login} post_html request send {call_num=} times {data=} {site_url=}")  # noqa: ERA001, E501
            if call_num >= 3:  # noqa: PLR2004
                self.result.headers.get("Content-Type")
                # standard_logger.debug(f"{self.login} post_html call_num >= 3 {call_num=} {content=}")  # noqa: ERA001
                text = f"{self.login}---post_html--error code: {self.result.status}"
                logger.error(f"{text=}")
                send_telegram(text)
                raise Exception(text)  # noqa: TRY002
            if auth:
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                answer = await self._session.post(site_url, data=data, headers=headers)
            else:
                answer = await self._session.post(site_url, data=data)
            # logger.critical(f"{answer.request_info=}")  # noqa: ERA001
            # for element in answer.request_info:
            if answer.status == status.HTTP_200_OK:
                return await answer.text()
                # logger.critical(f"{answer.__dict__=}")  # noqa: ERA001
            elif answer.status == status.HTTP_502_BAD_GATEWAY:  # noqa: RET505
                text = f"{self.login} post_html Error {answer.status=}"
                # standard_logger.error(f"{self.login} Retry POST query 502 {data=} and {site_url=}")  # noqa: ERA001
                send_telegram(text)
                logger.error(f"{self.login} Retry POST query 502 {data=} and {site_url=}")
                raise Exception(text)  # noqa: TRY002
            else:
                text = f"{self.login} ---post_html--error code: {answer.status=}"
                send_telegram(text)
                # standard_logger.error(f"post_html something new  {call_num=}")  # noqa: ERA001
                raise Exception(text)  # noqa: TRY002

        try:
            return await _retry(data)
        except Exception as error:  # noqa: BLE001
            # request_log_text = f"{self.login}\n{self.result.status=}\n"  # noqa: ERA001
            # request_log_text += f"{site_url=}\n"  # noqa: ERA001
            # request_log_text += f"{type(data)} {data=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.text=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.content=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.headers=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.reason=}\n"  # noqa: ERA001
            # request_log_text += f"{self.result.request.body=}\n"  # noqa: ERA001
            # standard_logger.warning(request_log_text)  # noqa: ERA001
            text = f"{self.login} post_html {error=}"
            logger.error(text)
            send_telegram(text)
            raise Exception(text)  # noqa: TRY002, B904
