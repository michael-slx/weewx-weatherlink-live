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

from typing import Dict

from user.weatherlink_live.static import config, labels

SHORT_SENSORS_TO_KEYS: Dict[str, config.SensorType] = {
    "th": config.SensorType.TEMPERATURE_HUMIDITY,
    "w": config.SensorType.WIND,
    "r": config.SensorType.RAIN,
    "s": config.SensorType.SOLAR,
    "u": config.SensorType.UV,
    "st1": config.SensorType.SOIL_TEMPERATURE_1,
    "st2": config.SensorType.SOIL_TEMPERATURE_2,
    "st3": config.SensorType.SOIL_TEMPERATURE_3,
    "st4": config.SensorType.SOIL_TEMPERATURE_4,
    "sm1": config.SensorType.SOIL_MOISTURE_1,
    "sm2": config.SensorType.SOIL_MOISTURE_2,
    "sm3": config.SensorType.SOIL_MOISTURE_3,
    "sm4": config.SensorType.SOIL_MOISTURE_4,
    "lw1": config.SensorType.LEAF_WETNESS_1,
    "lw2": config.SensorType.LEAF_WETNESS_2,
}

SENSOR_KEYS_TO_SHORT: Dict[config.SensorType, str] = {sensor_key: short
                                                      for short, sensor_key
                                                      in SHORT_SENSORS_TO_KEYS.items()}

SHORT_SENSORS_DESCRIPTION: Dict[str, str] = {sensor_short: labels.SENSOR_LABELS[sensor_key]
                                             for sensor_short, sensor_key
                                             in SHORT_SENSORS_TO_KEYS.items()}
