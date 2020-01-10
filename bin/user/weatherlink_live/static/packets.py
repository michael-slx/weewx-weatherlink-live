from enum import IntEnum


class DataStructureType(IntEnum):
    ISS = 1
    LEAF_SOIL = 2
    WLL_BARO = 3
    WLL_TH = 4


KEY_DEVICE_ID = "did"
KEY_DEVICE_NAME = "name"
KEY_TS = "ts"
KEY_CONDITIONS = "conditions"
KEY_DATA_STRUCTURE_TYPE = "data_structure_type"
KEY_TRANSMITTER_ID = "txid"

KEY_TEMPERATURE = "temp"
KEY_HUMIDITY = "hum"
KEY_DEW_POINT = "dew_point"
KEY_WET_BULB = "wet_bulb"
KEY_HEAT_INDEX = "heat_index"
KEY_WIND_CHILL = "wind_chill"
KEY_THW_INDEX = "thw_index"
KEY_THSW_INDEX = "thsw_index"
KEY_WIND_SPEED = "wind_speed_last"
KEY_WIND_DIR = "wind_dir_last"
KEY_RAIN_SIZE = "rain_size"
KEY_RAIN_RATE = "rain_rate_last"
KEY_RAIN_AMOUNT_DAILY = "rainfall_daily"
KEY_SOLAR_RADIATION = "solar_rad"
KEY_UV_INDEX = "uv_index"

KEY_TEMPERATURE_LEAF_SOIL = "temp_%{n}"
KEY_SOIL_MOISTURE = "moist_soil_%{n}"
KEY_LEAF_WETNESS = "wet_leaf_%{n}"

KEY_TEMPERATURE_INDOOR = "temp_in"
KEY_HUMIDITY_INDOOR = "hum_in"
KEY_DEW_POINT_INDOOR = "dew_point_in"
KEY_HEAT_INDEX_INDOOR = "heat_index_in"

KEY_BARO_ABSOLUTE = "bar_absolute"
KEY_BARO_SEA_LEVEL = "bar_sea_level"
