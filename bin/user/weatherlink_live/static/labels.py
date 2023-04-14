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

"""
Labels for displaying mappings
"""
from typing import Dict

from user.weatherlink_live.static import config

LABEL_SOURCE_TX_ID = "Transmitter %d"
LABEL_SOURCE_WLL_BAROMETER = "Barometer"
LABEL_SOURCE_WLL_TH = "Indoor"

LABEL_TEMPERATURE = "Temperature"
LABEL_HUMIDITY = "Humidity"
LABEL_DEW_POINT = "Dew point"
LABEL_WET_BULB = "Wet bulb"
LABEL_HEAT_INDEX = "Heat index"
LABEL_WIND_CHILL = "Wind chill"
LABEL_THW_INDEX = "THW index"
LABEL_THSW_INDEX = "THSW index"
LABEL_WIND_SPEED = "Current wind speed"
LABEL_WIND_DIR = "Current wind direction"
LABEL_WIND_GUST_SPEED = "Wind gust speed"
LABEL_WIND_GUST_DIR = "Wind gust direction"
LABEL_RAIN_AMOUNT = "Rain amount"
LABEL_RAIN_RATE = "Rain rate"
LABEL_RAIN_COUNT = "Number of times the rain measuring spoon tipped"
LABEL_RAIN_COUNT_RATE = "Rate the rain measuring spoon is tipping"
LABEL_RAIN_SIZE = "Size of rain measuring spoon"
LABEL_SOLAR_RADIATION = "Solar radiation"
LABEL_UV_INDEX = "UV index"

LABEL_SOIL_TEMPERATURE = "Agricultural temperature %d"
LABEL_SOIL_MOISTURE = "Agricultural moisture %d"
LABEL_LEAF_WETNESS = "Leaf wetness %d"

LABEL_TEMPERATURE_INDOOR = "Indoor temperature"
LABEL_HUMIDITY_INDOOR = "Indoor humidity"
LABEL_DEW_POINT_INDOOR = "Indoor dew point"
LABEL_HEAT_INDEX_INDOOR = "Indoor heat index"

LABEL_BARO_ABSOLUTE = "Barometer (absolute)"
LABEL_BARO_SEA_LEVEL = "Barometer (sea level)"

LABEL_BATTERY_STATUS = "Battery status"

SENSOR_LABELS: Dict[str, str] = {
    config.SENSOR_TYPE_TEMPERATURE_HUMIDITY: "Temperature/Humidity",
    config.SENSOR_TYPE_RAIN: "Rain",
    config.SENSOR_TYPE_WIND: "Wind",
    config.SENSOR_TYPE_SOLAR: "Solar irradiation",
    config.SENSOR_TYPE_UV: "UV index",
    config.SENSOR_TYPE_SOIL_TEMPERATURE: "Soil temperature",
    config.SENSOR_TYPE_SOIL_MOISTURE: "Soil moisture",
    config.SENSOR_TYPE_LEAF_WETNESS: "Leaf wetness",
}
