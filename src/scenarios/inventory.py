import pickle
import re
from datetime import UTC
from datetime import datetime
from enum import Enum
from pathlib import Path

from loguru import logger
from pydantic import BaseModel
from pydantic import Field

from src.config.config import settings
from src.config.consts.url import URL_MAIN
from src.scenarios.nl_request.connection import connect
from src.scenarios.nl_request.request_to_nl import Connection
from src.utils.inventory import MATCH_DICT
from src.utils.inventory import find_elements
from src.utils.inventory import get_dungeon_elements


FIND_IN_CITY = r"(?<=Инвентарь\" onclick=\"location=\'main\.php\?).+(?=\'\">)"

FIND_FROM_NATURE_TO_INV = r"(?<=Инвентарь\",\")\w+(?=\",\[\]\]|\",\[\]\],)"

FIND_PAGE_INVENTAR = r"(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)"


END_CELL = r"</td></tr></table></td></tr></table></td></tr>"

START_CELL = r"<tr><td bgcolor=#F5F5F5><div align=center>"

ELIXIR = r"http://neverlands.ru/main.php?im=6"


class Location(str, Enum):
    CITY = "CITY"
    FIGHT = "FIGHT"
    INVENTAR = "INVENTAR"
    NATURE = "NATURE"
    ELIXIR = "ELIXIR"
    INFO = "INFO"


def _find_pattern(pattern: str, string: str | None = None) -> list:
    return re.findall(pattern, string)


async def from_city_to_inventar(connect: Connection, html: str) -> str:
    """Construct the request and send it."""
    logger.success("in city")
    prepare = _find_pattern(FIND_IN_CITY, html)
    vcode = prepare[0].split("=")[-1]
    data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
    # TODO: need do retry get
    return await connect.get_html(URL_MAIN, data=data)


async def from_nature_to_inventar(connect: Connection, html: str) -> str:
    """Construct the request and send it."""
    logger.success("in nature")
    prepare = _find_pattern(FIND_FROM_NATURE_TO_INV, html)
    logger.debug(f"{prepare=}")
    result = ""
    if prepare:
        request_data = {"get_id": "56", "act": "10", "go": "inv", "vcode": prepare[0]}
        # TODO: need do retry get
        result = await connect.get_html(URL_MAIN, data=request_data)

    return result


async def from_info_to_inventar(connect: Connection, html: str) -> str:
    """Construct the request and send it."""
    logger.success("in info")

    logger.debug("not self.prepare")
    new_prepare = _find_pattern(FIND_PAGE_INVENTAR, html)
    result = ""
    if new_prepare:
        vcode = new_prepare[0].split("=")[-1]
        data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
        # TODO: need do retry get
        result = await connect.get_html(URL_MAIN, data=data)
    else:
        logger.debug('from_info_to_inventar not find ?<=&go=inv&vcode=).+(?=\'" value="Инвентарь')

    return result


async def from_elixir_to_inventar(connect: Connection, html: str) -> str:  # noqa: ARG001
    """Construct the request and send it."""
    logger.success("in elixir")
    site_url = "http://www.neverlands.ru/main.php?wca=28"
    # TODO: need do retry get
    return await connect.get_html(site_url)


async def do_nothing(connect: Connection, html: str) -> str:  # noqa: ARG001
    """Do nothing."""
    return "Do nothing."


async def go_to_elixir(connect: Connection) -> str:
    logger.success("go to elixir")
    return await connect.get_html(ELIXIR)


async def switch_to_inventory(connect: Connection) -> str:
    """Switch to inventory or fight and switch."""
    logger.info("def switch_to_inventory")

    # TODO: need do retry get
    html = await connect.get_html(URL_MAIN)
    location = where_i_am(html)
    logger.success(f"{location.value=}")
    location_to_inventory = {
        Location.FIGHT.value: do_nothing,
        Location.CITY.value: from_city_to_inventar,
        Location.NATURE.value: from_nature_to_inventar,
        Location.INVENTAR.value: do_nothing,
        Location.ELIXIR.value: from_elixir_to_inventar,
        Location.INFO.value: from_info_to_inventar,
    }
    return await location_to_inventory[location.value](connect, html)


def where_i_am(html: str) -> Location:
    """Where i am."""
    """
        При входе может находится перс на 3х этапах
        1 - инфо
        2 - инвентарь
        3 - природа ну или город
        """
    # html = connect.get_html()

    # # Just test!!!!  WORK!!!!
    # person_info = get_info()
    # parameters.update_params(person_info)
    # parameter = parameters.parse()
    # logger.success(f"{parameter=}")

    # connect.make_file(html, "first_check")
    if "var param_en" in html:
        logger.success("in fight")
        # location = "fight"
        return Location.FIGHT

    if "DISABLED" not in html:
        logger.success("on nature")
        # location = "nature"
        return Location.NATURE

    if '"Инвентарь" DISABLED>' in html:
        # # TODO: refactoring
        """ELIXIR have the same as invetar but not"""
        logger.success("in inventar")
        # connect.make_file(html, "Not_inventar")
        # location = "inventar"
        return Location.INVENTAR

    # pattern = r"(?<=Инвентарь\" onclick=\"location=\'main\.php\?).+(?=\'\">)"  # in city
    # pattern = r'(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)'  # mb oktal
    # pattern = FIND_IN_CITY
    # prepare = re.findall(pattern, html)
    prepare = _find_pattern(FIND_IN_CITY, html)
    logger.debug(f"{prepare=}")
    if prepare:
        logger.success("in city")
        return Location.CITY

    # pattern = r"(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)"
    # pattern = FIND_PAGE_INVENTAR
    # prepare = re.findall(pattern, html)
    prepare = _find_pattern(FIND_PAGE_INVENTAR, html)
    if not prepare:
        logger.success("in elixir")
        return Location.ELIXIR

    logger.success("in info")
    return Location.INFO


def make_html_file(text: str, reason: str) -> None:
    now = datetime.now(tz=UTC).strftime("%d-%m-%Y %H:%M:%S")
    dir_path = Path(__file__).parent.resolve()
    file_name = f"{now}_{reason}"
    file_path = Path(dir_path) / "files" / f"{file_name}.html"
    # file_path = os.path.join(dir_path, "files", f"{file_name}.html")

    # with open(file_path, "w", encoding="cp1251") as file:

    with Path(file_path).open("w") as file:
        file.write(text)


def make_file(text: str, reason: str) -> None:
    # now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # dir_path = Path(__file__).parent.resolve()
    # file_name = f"{now}_{reason}_{settings.person.LOGIN}"
    # file_path = os.path.join(dir_path, "files", f"{file_name}.txt")

    file_path = f"tests_files/{reason}.txt"
    with Path(file_path).open("w") as file:
        file.write(text)


async def get_inventory(connection: Connection) -> str:
    result = await switch_to_inventory(connection)
    await connection.close()
    make_file(result, "inventory")

    return result


needed_elements = [
    "Отпирающее заклинание",
    "Обрывки свитка с заклинанием",
    "Превосходное Зелье Лечения",
    "Превосходное Зелье Маны",
    "Свиток Величия",
    "Древний Свиток Величия",
    "Слеза Создателя",
    "Свиток каменной кожи",
    "Праздничная Слеза Создателя",
    "Гнев Локара",
    "Зелье Человек-Гора",
    "Превосходное Зелье Человек-Гора",
    "Зелье Панциря",
    "Превосходное Зелье Панциря",
    "Эликсир Быстроты",
    "Молодильное яблочко",
    "Мандарин",
]


class Item(BaseModel):
    name: str = Field(title="Name")
    count: int = Field(title="Количество")
    translated_name: str = Field(title="Название")


async def get_inventory_client() -> str:
    connection = await connect()

    result = await switch_to_inventory(connection)
    # make_html_file(result, "inventory")
    elements = find_elements(result)
    result_part1 = get_dungeon_elements(elements, needed_elements)

    result2 = await go_to_elixir(connection)
    # make_html_file(result2, "elixir")
    elements2 = find_elements(result2)
    result_part2 = get_dungeon_elements(elements2, needed_elements, result_part1)
    logger.success(f"{result_part2=}")

    all_elements = {**elements, **elements2}
    make_file(str(all_elements), "all_elements")

    make_file(str(result_part2), "result")

    new_list = []
    for name, count in all_elements.items():
        translated_name = MATCH_DICT[name]
        new_list.append(Item(name=name, count=count, translated_name=translated_name))
    with Path("items.pkl").open("wb") as file:  # noqa: ASYNC101
        pickle.dump(new_list, file)

    await connection.close()
    return result_part2


class LoginForm(BaseModel):
    cookie: str
    login: str
    password: str
    proxy_ip: str
    proxy_port: str
    proxy_log: str
    proxy_pass: str


def update_settings(form: LoginForm) -> None:
    new_dict = form.model_dump()
    login_form = LoginForm(**new_dict)
    settings.person.LOGIN = login_form.login
    settings.person.PASSWORD = login_form.password
    settings.person.COOKIE = login_form.cookie
    settings.connection.PROXY_IP = login_form.proxy_ip
    settings.connection.PROXY_PORT = login_form.proxy_port
    settings.connection.PROXY_LOG = login_form.proxy_log
    settings.connection.PROXY_PASS = login_form.proxy_pass
    # print(f"{settings=}")
