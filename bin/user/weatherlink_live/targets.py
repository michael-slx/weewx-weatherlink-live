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

# WIND
WIND_GUST_SPEED = ["windGust"]
WIND_GUST_DIR = ["windGustDir"]
WIND_SPEED = ["windSpeed"]
WIND_DIR = ["windDir"]

# RAIN
RAIN_AMOUNT = ["rain"]
RAIN_RATE = ["rainRate"]

# SOLAR
SOLAR_RADIATION = ["radiation"]

# UV
UV = ["UV"]

# WINDCHILL
WINDCHILL = ["windchill"]

# THW
THW = ["thw"]

# THSW
THSW = ["thsw"]

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
LEAF_TEMP = {"leafTemp1", "leafTemp2"}

# LEAF WETNESS
LEAF_WETNESS = {"leafWet1", "leafWet2"}

# WLL Thermo/Hygro (Indoor)
INDOOR_TEMP = ["inTemp"]
INDOOR_HUM = ["inHumidity"]
INDOOR_DEW_POINT = ["inDewpoint"]
INDOOR_HEAT_INDEX = ["inHeatindex"]

# WLL Baro
BARO_ABSOLUTE = ["pressure"]
BARO_SEA_LEVEL = ["altimeter"]  # the WLL doesn't use temperature to calculate sea level pressure

# AIRLINK PM
# AirLink's TH sensor is treated like any TH sensor
PM1 = ["pm1_0"]
PM2p5 = ["pm2_5"]
PM10 = ["pm10_0"]
