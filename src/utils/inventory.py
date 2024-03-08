import re
from collections import defaultdict


END_CELL = r"</td></tr></table></td></tr></table></td></tr>"

START_CELL = r"<tr><td bgcolor=#F5F5F5><div align=center>"

REGEXP = r"(?<=<tr><td bgcolor=#F5F5F5><div align=center>)(.*?)(?=</td></tr></table></td></tr></table></td></tr>)"


quiz = r"http://neverlands.ru/main.php?wca=60"

# scrolls
scrolls = r"http://neverlands.ru/main.php?wca=28"

elixir = r"http://neverlands.ru/main.php?im=6"

NAME = r"(?<=<font class=nickname><b>)(.*?)(?=</b>)"

NAME_WITH_ELEMENTS = r"(?<=<font class=nickname><b>)(.*?)(?=Масса: <b>)"

NAME_WITH_ELEMENTS3 = r"(?<=<font class=nickname><b>)(.*?<)(.*?)(Долговечность: <b>.*?)(</b>.*?)(?=Масса: <b>)"

file_path = "/home/anton/PetProject/NL/fast_ui_never/src/scenarios/files/18-02-2024 07:33:59_inventory_green.txt"


def read_file(file_path) -> str:
    with open(file_path) as file:
        return file.read()


def find_unique_elements() -> list[str]:
    text = read_file(file_path)
    result = re.findall(NAME, text)
    elements = set()
    elements.update(result)
    return elements


def find_elements(html: str) -> dict[str, int]:
    result = re.findall(NAME_WITH_ELEMENTS3, html)
    elements = defaultdict(int)
    for element in result:
        elements[element[0].strip().replace("<", "")] += int(element[2].replace("Долговечность: <b>", "").split("/")[0])

    return elements


def get_dungeon_elements(
    elements: dict[str, int],
    needed_elements: list[str],
    elements_dict: dict | None = None,
) -> dict[str, int]:
    new = elements_dict if elements_dict else defaultdict(int)
    for name in needed_elements:
        if name in elements:
            new[name] += elements[name]
    return new


TRANSLATED_NAMES = {
    "Poison": "Яд",
    "Scroll of Greatness": "Свиток Величия",
    "Combat First Aid Kit": "Боевая аптечка",
    "Assault Permit IV": "Разрешение на нападение IV",
    "Glove Blueprint Fragment I": "Обрывок чертежей перчаток I",
    "Superior Shell Potion": "Превосходное Зелье Панциря",
    "Beginner Healer's Bag": "Сумка начинающего лекаря",
    "Superior Strong Back Potion": "Превосходное Зелье Сильной Спины",
    "Superior Man-Mountain Potion": "Превосходное Зелье Человек-Гора",
    "Teleport (Dead Marsh)": "Телепорт (Гиблая Топь)",
    "Ancient Scroll of Greatness": "Древний Свиток Величия",
    "Elixir of Swiftness": "Эликсир Быстроты",
    "Rat Tail": "Крысиный хвост",
    "Scroll of Combat Termination": "Свиток завершения боя",
    "Bait For Bots": "Приманка Для Ботов",
    "Staff Blueprint Fragment I": "Обрывок чертежей посоха I",
    "Wrath of Lokar": "Гнев Локара",
    "Golden Doctor's Badge": "Золотой знак доктора",
    "Scroll of Distorting Mist": "Свиток Искажающего Тумана",
    "Glove Blueprint Fragment III": "Обрывок чертежей перчаток III",
    "Machete": "Мачете",
    "Bracers Blueprint Fragment III": "Обрывок чертежей наручей III",
    "Scroll of Earth Magic": "Свиток Магии Земли",
    "Large Unknown Potion": "Большое неизвестное зелье",
    "Gladiator's Scroll": "Свиток Гладиатора",
    "Order of the Dragon Bracers": "Наручи Ордена Дракона",
    "Stone Skin Scroll": "Свиток каменной кожи",
    "Defense Scroll III": "Свиток Защиты III",
    "Closed Fist Assault": "Закрытое кулачное нападение",
    "Bracers Blueprint Fragment IV": "Обрывок чертежей наручей IV",
    "Elixir of Bliss": "Эликсир Блаженства",
    "Experienced Healer's Bag": "Сумка опытного лекаря",
    "Festive Creator's Tear": "Праздничная Слеза Создателя",
    "Bracers Blueprint Fragment II": "Обрывок чертежей наручей II",
    "Dungeon Coin": "Монета из подземелья",
    "Superior Healing Potion": "Превосходное Зелье Лечения",
    "Superior Mana Potion": "Превосходное Зелье Маны",
    "Summon Imp Assistant": "Призыв импа-помощника",
    "Invisibility Dispersion": "Рассеивание невидимости",
    "Scroll of Closed Assault": "Свиток закрытого нападения",
    "Creator's Tear": "Слеза Создателя",
    "Closed Combat Assault": "Закрытое боевое нападение",
    "Ice Elixir I": "Ледяной эликсир I",
    "Champagne Bottle": "Бутылка Шампанского",
    "Potion of Sharpness": "Зелье Колкости",
    "Teleport": "Телепорт",
    "Elementalist Potion": "Зелье Элементалиста",
    "Iris's Cup": "Чаша Айрис",
    "Berserk Scroll": "Свиток Берсерка",
    "Elixir of Instant Healing": "Эликсир Мгновенного Исцеления",
    "Shell Potion": "Зелье Панциря",
    "Combat Assault": "Боевое нападение",
    "Order of the Dragon Boots": "Сапоги Ордена Дракона",
    "Time Loop": "Петля Времени",
    "Youthful Apple": "Молодильное яблочко",
    "Ice Elixir II": "Ледяной эликсир II",
    "Chicory Schnapps": "Жихорийский шнапс",
    "Scroll of Fire Magic": "Свиток Магии Огня",
    "Scroll of Detection": "Свиток Обнаружения",
    "Glove Blueprint Fragment IV": "Обрывок чертежей перчаток IV",
    "Glove Blueprint Fragment II": "Обрывок чертежей перчаток II",
    "Man-Mountain Potion": "Зелье Человек-Гора",
    "Siege Scroll": "Свиток Осады",
    "Teleport (Fort of Ringing Leaves)": "Телепорт (Форт Звенящей Листвы)",
    "Elixir of Restoration": "Эликсир Восстановления",
    "Defense Scroll I": "Свиток Защиты I",
    "Berserk Rage Potion": "Зелье Ярость Берсерка",
    "Experienced Healer's Bag II": "Сумка опытного лекаря II",
    "Bloodthirst Potion": "Зелье Кровожадности",
    "Potion of Miraculous Recovery": "Зелье чудесного восстановления",
    "Staff Blueprint Fragment II": "Обрывок чертежей посоха II",
    "Gems": "Самоцветы",
    "Staff Blueprint Fragment III": "Обрывок чертежей посоха III",
    "Silver Doctor's Badge": "Серебряный знак доктора",
    "Scroll of Exile from Battle": "Свиток Изгнания из боя",
    "Staff Blueprint Fragment IV": "Обрывок чертежей посоха IV",
    "Scroll of Patronage (3 hours)": "Свиток Покровительства (3 часа)",
    "Scroll of Inevitability (3 hours)": "Свиток Неизбежности (3 часа)",
    "Amber Pearl": "Янтарный жемчуг",
    "Portal": "Портал",
}

MATCH_DICT = {}

for key, value in TRANSLATED_NAMES.items():
    MATCH_DICT[value] = key
