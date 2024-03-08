from enum import Enum
from enum import IntEnum


class PersonRole(IntEnum):
    SLAVE = 0
    LEADER = 1
    SOLO = 2


class PersonType(IntEnum):
    WARRIOR = 0
    MAG = 1


class Location(str, Enum):
    CITY = "CITY"
    FIGHT = "FIGHT"
    INVENTAR = "INVENTAR"
    NATURE = "NATURE"
    ELIXIR = "ELIXIR"
    INFO = "INFO"


class Teleport(IntEnum):
    FP = 1
    OKTAL = 2
    PODGORN = 3
    OKREST_FEIDANA = 4
    OKREST_OKTAL = 5
    OKREST_ERINGARD = 6
    OKREST_FP = 7
    SAMYM_BEYT = 8
    NORTHERN_TRACT = 9
    EASTERN_FORESTS = 10
    OKREST_KENGI = 11
    GORGE_EL_TER = 12
