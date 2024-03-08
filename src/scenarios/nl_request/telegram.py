import requests
from fastapi import status
from loguru import logger

from src.config.config import settings


def send_telegram(text: str) -> None:
    method = "https://api.telegram.org/bot" + settings.message.TG_TOKEN + "/sendMessage"
    if settings.message.CHANNEL_ID:
        result = requests.post(
            method,
            data={
                "chat_id": settings.message.CHANNEL_ID,
                "text": text,
            },
            timeout=10,
        )
        logger.debug(f"{settings.message.CHANNEL_ID=}")
        if result.status_code != status.HTTP_200_OK:
            logger.critical("Some trouble with TG")

    if settings.message.CHANNEL_ID_FRIENDS or settings.message.CHANNEL_ID_LEADER:
        logger.debug("if CHANNEL_ID_FRIENDS:")
        lst_id = settings.message.CHANNEL_ID_FRIENDS.split(",")
        leader = settings.message.CHANNEL_ID_LEADER
        if leader and leader not in lst_id and leader != settings.message.CHANNEL_ID:
            lst_id.append(settings.message.CHANNEL_ID_LEADER)
        for chanel_id in lst_id:
            logger.debug(f"{chanel_id=}")
            query = requests.post(
                method,
                data={
                    "chat_id": chanel_id,
                    "text": text,
                },
                timeout=10,
            )
            if query.status_code != status.HTTP_200_OK:
                logger.critical("Some trouble with TG")
