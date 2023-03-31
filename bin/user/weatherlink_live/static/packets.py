# Copyright © 2020-2023 Michael Schantl and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
KEY_BATTERY_FLAG = "trans_battery_flag"

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

KEY_TEMPERATURE_LEAF_SOIL = "temp_%d"
KEY_SOIL_MOISTURE = "moist_soil_%d"
KEY_LEAF_WETNESS = "wet_leaf_%d"

KEY_TEMPERATURE_INDOOR = "temp_in"
KEY_HUMIDITY_INDOOR = "hum_in"
KEY_DEW_POINT_INDOOR = "dew_point_in"
KEY_HEAT_INDEX_INDOOR = "heat_index_in"

KEY_BARO_ABSOLUTE = "bar_absolute"
KEY_BARO_SEA_LEVEL = "bar_sea_level"
