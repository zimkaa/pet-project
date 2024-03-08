import aiohttp
from pydantic import Field
from pydantic import computed_field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from src.config.consts import connection
from src.config.consts import name
from .types import PersonRole
from .types import PersonType


class ConnectionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CHECKER_IP_SITE: str = Field(default="http://ipinfo.io/ip")
    SERVER_IP: str = Field(default="")

    PROXY: bool = Field(default=True)
    PROXY_IP: str = Field(default="")
    PROXY_LOG: str = Field(default="empty")
    PROXY_PASS: str = Field(default="empty")
    PROXY_PORT: str = Field(default="empty")

    @computed_field
    @property
    def PROXIES(self) -> dict[str, str]:  # noqa: N802
        proxies: dict[str, str] = {
            "http": f"http://{self.PROXY_LOG}:{self.PROXY_PASS}@{self.PROXY_IP}:{self.PROXY_PORT}",
            "https": f"https://{self.PROXY_LOG}:{self.PROXY_PASS}@{self.PROXY_IP}:{self.PROXY_PORT}",
        }
        return proxies

    HEADER: dict[str, str] = Field(default=connection.HEADER)


class SendMessageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CHANNEL_ID: str = Field(default="277594923")

    CHANNEL_ID_FRIENDS: str = Field(default="")

    CHANNEL_ID_ROMANSON: str = Field(default="")

    CHANNEL_ID_HUNTER: str = Field(default="")

    CHANNEL_ID_TURNOFF: str = Field(default="")

    CHANNEL_ID_ANGEL: str = Field(default="")

    CHANNEL_ID_ABYSS: str = Field(default="")

    CHANNEL_ID_LEGALAS: str = Field(default="")

    CHANNEL_ID_LEADER: str = Field(default="")

    TG_TOKEN: str = Field(default="")


class DungeonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AUTO_BUFF: bool = Field(default=True)

    PERSON_ROLE: PersonRole = Field(default=PersonRole.SLAVE)

    LEADER_NAME: str = Field(default=name.LEGALAS)
    LEADER_TYPE: PersonType = Field(default=PersonType.WARRIOR)

    DUNGEON_WATCHER: str = Field(default=name.LEGALAS)

    MAG_KILLER: bool = Field(default=True)

    PERSON_TYPE: PersonType = Field(default=PersonType.MAG)

    # TODO: GET FROM DUNGEON  # noqa: FIX002, TD003, TD002
    PARTY_MEMBERS: list[str] = Field(default=[name.TURNOFF, name.LEGALAS])

    @computed_field
    @property
    def LEN_PARTY(self) -> int:  # noqa: N802
        return len(self.PARTY_MEMBERS)

    MAG_DAMAGER: str = Field(default=name.TURNOFF)


class PersonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOGIN: str
    PASSWORD: str

    COOKIE: str = Field(default="")

    @computed_field
    @property
    def NICKNAME(self) -> str:  # noqa: N802
        return self.LOGIN

    @computed_field
    @property
    def DATA(self) -> aiohttp.FormData:  # noqa: N802
        form_data = aiohttp.FormData(charset="windows-1251")
        form_data.add_field("player_nick", self.LOGIN)
        form_data.add_field("player_password", self.PASSWORD)
        return form_data


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SIEGE: bool = Field(default=False)

    dungeon: DungeonSettings = Field(default=DungeonSettings())

    FIGHT_ITERATIONS: int = Field(default=5)

    SLEEP_TIME: float = Field(default=5)

    SLEEP_TIME_PER_HIT: float = Field(default=0.5)

    FIGHT_TEST_MODE: bool = Field(default=False)

    AB: bool = Field(default=True)

    connection: ConnectionSettings = Field(default=ConnectionSettings())

    CITY: str = Field(default="2")

    TELEPORT_CITY: int = Field(default=2)  # OKTAL

    SIEGE_DRESS: str = Field(default="Маг")  # noqa: RUF001

    HOME_DIR: str = Field(default=".\\files")

    FLOOR: str = Field(default="99")

    message: SendMessageSettings = Field(default=SendMessageSettings())

    person: PersonSettings = Field(default=PersonSettings())

    @computed_field
    @property
    def CHANNEL_ID_LEADER(self) -> str:  # noqa: N802
        channel_dict: dict[str, str] = {
            name.ROMANSON: self.message.CHANNEL_ID_ROMANSON,
            name.HUNTER: self.message.CHANNEL_ID_HUNTER,
            name.TURNOFF: self.message.CHANNEL_ID_TURNOFF,
            name.ANGEL: self.message.CHANNEL_ID_ANGEL,
            name.ABYSS: self.message.CHANNEL_ID_ABYSS,
            name.LEGALAS: self.message.CHANNEL_ID_LEGALAS,
        }
        if self.dungeon.PERSON_ROLE == PersonRole.SLAVE:
            channel = channel_dict.get(self.dungeon.DUNGEON_WATCHER, "")
        else:
            channel = ""
        return channel


settings = Settings()
