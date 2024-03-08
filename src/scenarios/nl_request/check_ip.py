import requests
from fastapi import status

from src.config.config import settings
from .telegram import send_telegram


class ProxyError(Exception):
    """PROXY DON'T RESPONSE!!!."""


def my_ip(proxies: dict | None = None) -> str:
    answer = requests.get(
        settings.connection.CHECKER_IP_SITE,
        headers=settings.connection.HEADER,
        proxies=proxies,
        timeout=10,
    )
    if answer.status_code != status.HTTP_200_OK:
        text = "PROXY DON'T RESPONSE!!!"
        send_telegram(text)
        raise ProxyError(text)
    return answer.text
