import os

from loguru import logger

from src.config.config import settings
from src.scenarios.nl_request.check_ip import my_ip
from src.scenarios.nl_request.request_to_nl import Connection


class WrongIPError(Exception):
    """Wrong IP."""


async def connect() -> Connection:
    if settings.connection.PROXY:
        login = settings.connection.PROXY_LOG
        password = settings.connection.PROXY_PASS
        port = settings.connection.PROXY_PORT
        ip = settings.connection.PROXY_IP
        proxy_url = f"http://{login}:{password}@{ip}:{port}"
        proxies = {
            "http": proxy_url,
        }
        real_ip = my_ip(proxies)
        os.environ.setdefault("HTTP_PROXY", proxy_url)
    else:
        real_ip = my_ip()

    if settings.connection.PROXY_IP in real_ip:
        logger.info(f"\n-------ip------- {real_ip} LOGIN {settings.person.NICKNAME}" * 5)
    else:
        logger.error(f"{settings.person.NICKNAME} {settings.connection.PROXY_IP=} not in real IP={real_ip}")
        msg = "Wrong IP or proxy not work"
        raise WrongIPError(msg)

    try:
        # logger.debug(f"{settings.connection.PROXY=}")  # noqa: ERA001
        connection = Connection(
            proxy=settings.connection.PROXY,
            login=settings.person.LOGIN,
            password=settings.person.PASSWORD,
        )
        await connection.start()
    except Exception as err:
        logger.error(f"{err=}")
        raise
    return connection
