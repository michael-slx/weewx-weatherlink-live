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

import enum

KEY_LOG_SUCCESS = 'log_success'
KEY_LOG_FAILURE = 'log_failure'

KEY_DRIVER_POLLING_INTERVAL = 'polling_interval'
KEY_DRIVER_HOST = "host"
KEY_DRIVER_MAPPING = 'mapping'
KEY_MAX_NO_DATA_ITERATIONS = "max_no_data_iterations"
KEY_SECTION_SENSORS = 'sensors'


class SensorType(enum.Enum):
    TEMPERATURE_HUMIDITY = 'temp_hum'
    RAIN = 'rain'
    WIND = 'wind'
    SOLAR = 'solar'
    UV = 'uv'
    SOIL_TEMPERATURE_1 = 'soil_temp_1'
    SOIL_TEMPERATURE_2 = 'soil_temp_2'
    SOIL_TEMPERATURE_3 = 'soil_temp_3'
    SOIL_TEMPERATURE_4 = 'soil_temp_4'
    SOIL_MOISTURE_1 = 'soil_moisture_1'
    SOIL_MOISTURE_2 = 'soil_moisture_2'
    SOIL_MOISTURE_3 = 'soil_moisture_3'
    SOIL_MOISTURE_4 = 'soil_moisture_4'
    LEAF_WETNESS_1 = 'leaf_wetness_1'
    LEAF_WETNESS_2 = 'leaf_wetness_2'

    # Adapted from https://stackoverflow.com/a/71839532/4644268
    def __lt__(self, other: 'SensorType') -> bool:
        if self == other:
            return False
        for elem in SensorType:
            if self == elem:
                return True
            elif other == elem:
                return False
        raise RuntimeError()


KEY_MAPPER_TEMPERATURE_ONLY = 't'
KEY_MAPPER_TEMPERATURE_HUMIDITY = 'th'
KEY_MAPPER_WIND = 'wind'
KEY_MAPPER_RAIN = 'rain'
KEY_MAPPER_SOLAR = 'solar'
KEY_MAPPER_UV = 'uv'
KEY_MAPPER_WINDCHILL = 'windchill'
KEY_MAPPER_THW = 'thw'
KEY_MAPPER_THSW = 'thsw'
KEY_MAPPER_SOIL_TEMP = 'soil_temp'
KEY_MAPPER_SOIL_MOIST = 'soil_moist'
KEY_MAPPER_LEAF_WETNESS = 'leaf_wet'
KEY_MAPPER_TH_INDOOR = 'th_indoor'
KEY_MAPPER_BARO = 'baro'
KEY_MAPPER_BATTERY = 'battery'
