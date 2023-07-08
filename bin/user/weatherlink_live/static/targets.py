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
Defaults for mapping sensors to observations
"""

# TH
TEMP = ["outTemp",
        "extraTemp1",
        "extraTemp2",
        "extraTemp3",
        "extraTemp4",
        "extraTemp5",
        "extraTemp6",
        "extraTemp7",
        "extraTemp8"]
HUM = ["outHumidity",
       "extraHumid1",
       "extraHumid2",
       "extraHumid3",
       "extraHumid4",
       "extraHumid5",
       "extraHumid6",
       "extraHumid7",
       "extraHumid8"]
DEW_POINT = ["dewpoint",
             "dewpoint1",
             "dewpoint2",
             "dewpoint3",
             "dewpoint4",
             "dewpoint5",
             "dewpoint6",
             "dewpoint7",
             "dewpoint8"]
HEAT_INDEX = ["heatindex",
              "heatindex1",
              "heatindex2",
              "heatindex3",
              "heatindex4",
              "heatindex5",
              "heatindex6",
              "heatindex7",
              "heatindex8"]
WET_BULB = ["wetbulb",
            "wetbulb1",
            "wetbulb2",
            "wetbulb3",
            "wetbulb4",
            "wetbulb5",
            "wetbulb6",
            "wetbulb7",
            "wetbulb8"]
APPARENT_TEMPERATURE = ["appTemp",
                        "appTemp1"]

# WIND
WIND_GUST_SPEED = ["windGust"]
WIND_GUST_DIR = ["windGustDir"]
WIND_SPEED = ["windSpeed"]
WIND_DIR = ["windDir"]

# RAIN
RAIN_AMOUNT = ["rain"]
RAIN_RATE = ["rainRate"]
RAIN_COUNT = ["rainCount"]
RAIN_COUNT_RATE = ["rainCountRate"]
RAIN_SIZE = ["rainSize"]

# SOLAR
SOLAR_RADIATION = ["radiation"]

# UV
UV = ["UV"]

# WINDCHILL
WINDCHILL = ["windchill"]

# THW
# Duplicated because we have two appTemp's too
THW = ["thw",
       "thw"]

# THSW
# Duplicated because we have two appTemp's too
THSW = ["thsw",
        "thsw"]

# SOIL TEMP
SOIL_TEMP = ["soilTemp1",
             "soilTemp2",
             "soilTemp3",
             "soilTemp4"]

# SOIL MOISTURE
SOIL_MOISTURE = ["soilMoist1",
                 "soilMoist2",
                 "soilMoist3",
                 "soilMoist4"]

# LEAF TEMP
LEAF_TEMP = ["leafTemp1", "leafTemp2"]

# LEAF WETNESS
LEAF_WETNESS = ["leafWet1", "leafWet2"]

# WLL Thermo/Hygrometer (Indoor)
INDOOR_TEMP = ["inTemp"]
INDOOR_HUM = ["inHumidity"]
INDOOR_DEW_POINT = ["inDewpoint"]
INDOOR_HEAT_INDEX = ["inHeatindex"]

# WLL Baro
BARO_ABSOLUTE = ["pressure"]
BARO_SEA_LEVEL = ["altimeter"]  # the WLL doesn't use temperature to calculate sea level pressure

# Battery status
BATTERY_STATUS = ['batteryStatus1',
                  'batteryStatus2',
                  'batteryStatus3',
                  'batteryStatus4',
                  'batteryStatus5',
                  'batteryStatus6',
                  'batteryStatus7',
                  'batteryStatus8']
BATTERY_STATUS_NAMED = {'outTemp': 'outTempBatteryStatus',
                        'rain': 'rainBatteryStatus',
                        'tx': 'txBatteryStatus',
                        'uv': 'uvBatteryStatus',
                        'wind': 'windBatteryStatus'}
