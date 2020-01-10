from enum import Enum


class PacketSource(Enum):
    WEATHER_POLL = 10
    WEATHER_PUSH = 20
