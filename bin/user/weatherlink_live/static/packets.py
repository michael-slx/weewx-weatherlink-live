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
import struct

class DataStructureType(IntEnum):
    ISS = 1
    LEAF_SOIL = 2
    WLL_BARO = 3
    WLL_TH = 4
    WLL_HEALTH = 15


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
KEY_GUST_SPEED = "wind_speed_hi"
KEY_GUST_DIR = "wind_speed_hi_dir"
KEY_RAIN_SIZE = "rain_size"
KEY_RAIN_RATE = "rain_rate_last"
KEY_RAIN_AMOUNT_DAILY = "rainfall_daily"
KEY_RAIN_AMOUNT = "rainfall"
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

KEY_ISS_BATTERY = "trans_battery"
KEY_ISS_PANEL = "solar_volt_last"
KEY_ISS_SUPERCAP = "supercap_volt_last"
KEY_WLL_BATTERY = "battery_voltage"
KEY_WLL_SUPPLY = "input_voltage"

WLC_START = 62869
WLC_END = 62633

WLC_SET_HISTRATE = b"*INF.DTXI"

LOOP_STA = ( ('temp',                  10,'h',     0x7fff), ('hum',                            10,'H',     0xffff),
        ('dew_point',                  10,'h',     0x7fff), ('wet_bulb',                       10,'h',     0x7fff),
        ('heat_index',                 10,'h',     0x7fff), ('wind_chill',                     10,'h',     0x7fff),
        ('thw_index',                  10,'h',     0x7fff), ('thsw_index',                     10,'h',     0x7fff),
        ('wind_speed_last',           100,'h',     0x7fff), ('wind_dir_last',                   1,'h',     0x7fff),
        ('wind_speed_avg_last_1_min', 100,'h',     0x7fff), ('wind_dir_scalar_avg_last_1_min',  1,'h',     0x7fff),
        ('wind_speed_avg_last_2_min', 100,'h',     0x7fff), ('wind_dir_scalar_avg_last_2_min',  1,'h',     0x7fff),
        ('wind_speed_hi_last_2_min',  100,'h',     0x7fff), ('wind_dir_at_hi_speed_last_2_min', 1,'h',     0x7fff),
        ('wind_speed_avg_last_10_min',100,'h',     0x7fff), ('wind_dir_scalar_avg_last_10_min', 1,'h',     0x7fff),
        ('wind_speed_hi_last_10_min', 100,'h',     0x7fff), ('wind_dir_at_hi_speed_last_10_min',1,'h',     0x7fff),
        ('rain_size',                   1,'B',       0xff), ('rain_rate_last',                  1,'H',     0xffff),
        ('rain_rate_hi',                1,'H',     0xffff), ('rainfall_last_15_min',            1,'H',     0xffff),
        ('rain_rate_hi_last_15_min',    1,'H',     0xffff), ('rainfall_last_60_min',            1,'H',     0xffff),
        ('rainfall_last_24_hr',         1,'H',     0xffff), ('rain_storm',                      1,'H',     0xffff),
        ('rain_storm_start_at',         1,'L', 0xffffffff), ('solar_rad',                       1,'H',     0xffff),
        ('uv_index',                    1,'B',       0xff), ('rx_state',                        1,'B',       0xff),
        ('trans_battery_flag',          1,'B',       0xff), ('rainfall_daily',                  1,'H',     0xffff),
        ('rainfall_monthly',            1,'H',     0xffff), ('rainfall_year',                   1,'H',     0xffff),
        ('rain_storm_last',             1,'H',     0xffff), ('rain_storm_last_start_at',        1,'L', 0xffffffff),
        ('rain_storm_last_end_at',      1,'L', 0xffffffff) )

LOOP_INT = (
        ('temp_in',     10,'h', 0x7fff), ('hum_in',       10,'H', 0xffff),
        ('dew_point_in',10,'h', 0x7fff), ('heat_index_in',10,'h', 0x7fff) )

LOOP_BAR = (
        ('bar_sea_level',1000,'H', 0xffff), ('bar_trend',1000,'h', 0x7fff),
        ('bar_absolute', 1000,'H', 0xffff) )

HIST_WLL = (
        ('health_version',    1,'B',       0xff), ('ww_fw_version',     1,'L', 0xffffffff),
        ('bluetooth_version', 1,'L', 0xffffffff), ('radio_version',     1,'L', 0xffffffff),
        ('espressif_version', 1,'L', 0xffffffff), ('battery_voltage',1000,'H',     0xffff),
        ('input_voltage',  1000,'H',     0xffff), ('uptime',            1,'L', 0xffffffff),
        ('bgn',               1,'B',       0xff), ('network_type',      1,'B',       0xff),
        ('ip_address_type',   1,'B',       0xff), ('ipv4_address',      1,'L', 0xffffffff),
        ('ipv4_gateway',      1,'L', 0xffffffff), ('ipv4_netmask',      1,'L', 0xffffffff),
        ('dns_used',          1,'B',       0xff), ('rx_bytes',          1,'L', 0xffffffff),
        ('tx_bytes',          1,'L', 0xffffffff), ('local_api_queries', 1,'L', 0xffffffff),
        ('rapid_records_sent',1,'L', 0xffffffff), ('wifi_rssi',         1,'b',      -0x80),
        ('link_uptime',       1,'L', 0xffffffff), ('network_error',     1,'H',     0xffff),
        ('touchpad_wakeups',  1,'H',     0xffff), ('bootloader_version',1,'L', 0xffffffff) )

HIST_STA = (
        ('interval',              1,'B',   0xff), ('temp',             10,'h', 0x7fff),
        ('temp_avg',             10,'h', 0x7fff), ('temp_hi',          10,'h',-0x8000),
        ('temp_hi_at',            1,'H', 0x7fff), ('temp_lo',          10,'h', 0x7fff),
        ('temp_lo_at',            1,'H', 0x7fff), ('hum',              10,'H', 0xffff),
        ('hum_hi',               10,'H', 0xffff), ('hum_hi_at',         1,'H', 0x7fff),
        ('hum_lo',               10,'H', 0xffff), ('hum_lo_at',         1,'H', 0x7fff),
        ('dew_point',            10,'h', 0x7fff), ('dew_point_hi',     10,'h',-0x8000),
        ('dew_point_hi_at',       1,'H', 0x7fff), ('dew_point_lo',     10,'h', 0x7fff),
        ('dew_point_lo_at',       1,'H', 0x7fff), ('wet_bulb',         10,'h', 0x7fff),
        ('wet_bulb_hi',          10,'h',-0x8000), ('wet_bulb_hi_at',    1,'H', 0x7fff),
        ('wet_bulb_lo',          10,'h', 0x7fff), ('wet_bulb_lo_at',    1,'H', 0x7fff),
        ('wind_speed_last',     100,'h', 0x7fff), ('wind_dir_last',     1,'h', 0x7fff),
        ('wind_speed_hi',       100,'h', 0x7fff), ('wind_speed_hi_dir', 1,'h', 0x7fff),
        ('wind_speed_hi_at',      1,'H', 0x7fff), ('wind_chill',       10,'h', 0x7fff),
        ('wind_chill_lo',        10,'h', 0x7fff), ('wind_chill_lo_at',  1,'H', 0x7fff),
        ('heat_index',           10,'h', 0x7fff), ('heat_index_hi',    10,'h',-0x8000),
        ('heat_index_hi_at',      1,'H', 0x7fff), ('thw_index',        10,'h', 0x7fff),
        ('thw_index_hi',         10,'h',-0x8000), ('thw_index_hi_at',   1,'H', 0x7fff),
        ('thw_index_lo',         10,'h', 0x7fff), ('thw_index_lo_at',   1,'H', 0x7fff),
        ('thsw_index',           10,'h', 0x7fff), ('thsw_index_hi',    10,'h',-0x8000),
        ('thsw_index_hi_at',      1,'H', 0x7fff), ('thsw_index_lo',    10,'h', 0x7fff),
        ('thsw_index_lo_at',      1,'H', 0x7fff), ('rain_size',         1,'B',   0xff),
        ('rainfall',              1,'H', 0xffff), ('rain_rate_hi',      1,'H', 0xffff),
        ('rain_rate_hi_at',       1,'H', 0x7fff), ('solar_rad',         1,'h',     -1),
        ('solar_rad_hi',          1,'h',     -1), ('solar_rad_hi_at',   1,'H', 0x7fff),
        ('unknown1',              1,'B',   0xff), ('uv_index',         10,'B',   0xff),
        ('uv_index_hi',          10,'B',   0xff), ('uv_index_hi_at',    1,'H', 0x7fff),
        ('solar_rad_volt_last',4000,'H', 0xffff), ('uv_volt_last',   1000,'H', 0xffff),
        ('reception',             1,'B',   0xff), ('rssi',              1,'b',  -0x80),
        ('error_packets',         1,'B',   0xff), ('resynchs',          1,'H', 0xffff),
        ('good_packets_streak',   1,'H', 0xffff), ('trans_battery_flag',1,'B',   0xff),
        ('trans_battery',      1000,'H', 0xffff), ('solar_volt_last',1000,'H', 0xffff),
        ('supercap_volt_last', 1000,'H', 0xffff), ('afc',               1,'h', 0x7fff) )

HIST_INT = (
        ('interval',      1,'B',   0xff), ('temp_in',     10,'h', 0x7fff),
        ('temp_in_hi',   10,'h',-0x8000), ('temp_in_hi_at',1,'H', 0x7fff),
        ('temp_in_lo',   10,'h', 0x7fff), ('temp_in_lo_at',1,'H', 0x7fff),
        ('hum_in',       10,'H', 0xffff), ('hum_in_hi',   10,'H', 0xffff),
        ('hum_in_hi_at',  1,'H', 0x7fff), ('hum_in_lo',   10,'H', 0xffff),
        ('hum_in_lo_at',  1,'H', 0x7fff), ('dew_point_in',10,'h', 0x7fff),
        ('heat_index_in',10,'h', 0x7fff) )

HIST_BAR = (
        ('interval',       1,'B',   0xff), ('bar_sea_level',1000,'H', 0xffff),
        ('bar_hi',      1000,'H', 0xffff), ('bar_hi_at',       1,'H', 0xffff),
        ('bar_lo',      1000,'H', 0xffff), ('bar_lo_at',       1,'H', 0xffff),
        ('bar_absolute',1000,'H', 0xffff) )

# XXX GUESSING...
HIST_LS = ( ('interval',       1,'B',   0xff), ('temp_last_1',       10,'h', 0x7fff),
        ('temp_hi_1',         10,'h', 0x7fff), ('temp_hi_at_1',       1,'H', 0xffff),
        ('temp_lo_1',         10,'h', 0x7fff), ('temp_lo_at_1',       1,'H', 0xffff),
        ('temp_last_2',       10,'h', 0x7fff), ('temp_hi_2',         10,'h', 0x7fff),
        ('temp_hi_at_2',       1,'H', 0xffff), ('temp_lo_2',         10,'h', 0x7fff),
        ('temp_lo_at_2',       1,'H', 0xffff), ('temp_last_3',       10,'h', 0x7fff),
        ('temp_hi_3',         10,'h', 0x7fff), ('temp_hi_at_3',       1,'H', 0xffff),
        ('temp_lo_3',         10,'h', 0x7fff), ('temp_lo_at_3',       1,'H', 0xffff),
        ('temp_last_4',       10,'h', 0x7fff), ('temp_hi_4',         10,'h', 0x7fff),
        ('temp_hi_at_4',       1,'H', 0xffff), ('temp_lo_4',         10,'h', 0x7fff),
        ('temp_lo_at_4',       1,'H', 0xffff), ('moist_soil_last_1',100,'h', 0x7fff),
        ('moist_soil_hi_1',  100,'h', 0x7fff), ('moist_soil_hi_at_1', 1,'H', 0xffff),
        ('moist_soil_lo_1',  100,'h', 0x7fff), ('moist_soil_lo_at_1', 1,'H', 0xffff),
        ('moist_soil_last_2',100,'h', 0x7fff), ('moist_soil_hi_2',  100,'h', 0x7fff),
        ('moist_soil_hi_at_2', 1,'H', 0xffff), ('moist_soil_lo_2',  100,'h', 0x7fff),
        ('moist_soil_lo_at_2', 1,'H', 0xffff), ('moist_soil_last_3',100,'h', 0x7fff),
        ('moist_soil_hi_3',  100,'h', 0x7fff), ('moist_soil_hi_at_3', 1,'H', 0xffff),
        ('moist_soil_lo_3',  100,'h', 0x7fff), ('moist_soil_lo_at_3', 1,'H', 0xffff),
        ('moist_soil_last_4',100,'h', 0x7fff), ('moist_soil_hi_4',  100,'h', 0x7fff),
        ('moist_soil_hi_at_4', 1,'H', 0xffff), ('moist_soil_lo_4',  100,'h', 0x7fff),
        ('moist_soil_lo_at_4', 1,'H', 0xffff), ('wet_leaf_last_1',    1,'h', 0x7fff),
        ('wet_leaf_hi_1',      1,'h', 0x7fff), ('wet_leaf_hi_at_1',   1,'H', 0xffff),
        ('wet_leaf_lo_1',      1,'h', 0x7fff), ('wet_leaf_lo_at_1',   1,'H', 0xffff),
        ('wet_leaf_min_1',     1,'h', 0x7fff), ('wet_leaf_last_2',    1,'h', 0x7fff),
        ('wet_leaf_hi_2',      1,'h', 0x7fff), ('wet_leaf_hi_at_2',   1,'H', 0xffff),
        ('wet_leaf_lo_2',      1,'h', 0x7fff), ('wet_leaf_lo_at_2',   1,'H', 0xffff),
        ('wet_leaf_min_2',     1,'h', 0x7fff) )

PACK_LOOP_STA = '<' + ''.join(list(zip(*LOOP_STA))[2])
PACK_LOOP_INT = '<' + ''.join(list(zip(*LOOP_INT))[2])
PACK_LOOP_BAR = '<' + ''.join(list(zip(*LOOP_BAR))[2])
PACK_HIST_WLL = '<' + ''.join(list(zip(*HIST_WLL))[2])
PACK_HIST_STA = '<' + ''.join(list(zip(*HIST_STA))[2])
PACK_HIST_INT = '<' + ''.join(list(zip(*HIST_INT))[2])
PACK_HIST_BAR = '<' + ''.join(list(zip(*HIST_BAR))[2])
PACK_HIST_LS  = '<' + ''.join(list(zip(*HIST_LS ))[2])

WLC_LOOP_STA = 100 + DataStructureType.ISS
WLC_LOOP_INT = 100 + DataStructureType.WLL_TH
WLC_LOOP_BAR = 100 + DataStructureType.WLL_BARO
WLC_HIST_WLL = DataStructureType.WLL_HEALTH
WLC_HIST_STA = DataStructureType.ISS
WLC_HIST_INT = DataStructureType.WLL_TH
WLC_HIST_BAR = DataStructureType.WLL_BARO
WLC_HIST_LS  = DataStructureType.LEAF_SOIL

packets = {
        WLC_LOOP_STA: ( LOOP_STA, PACK_LOOP_STA, struct.calcsize(PACK_LOOP_STA) ),
        WLC_LOOP_INT: ( LOOP_INT, PACK_LOOP_INT, struct.calcsize(PACK_LOOP_INT) ),
        WLC_LOOP_BAR: ( LOOP_BAR, PACK_LOOP_BAR, struct.calcsize(PACK_LOOP_BAR) ),
        WLC_HIST_STA: ( HIST_STA, PACK_HIST_STA, struct.calcsize(PACK_HIST_STA) ),
        WLC_HIST_INT: ( HIST_INT, PACK_HIST_INT, struct.calcsize(PACK_HIST_INT) ),
        WLC_HIST_BAR: ( HIST_BAR, PACK_HIST_BAR, struct.calcsize(PACK_HIST_BAR) ),
        WLC_HIST_WLL: ( HIST_WLL, PACK_HIST_WLL, struct.calcsize(PACK_HIST_WLL) ),
        WLC_HIST_LS:  ( HIST_LS,  PACK_HIST_LS,  struct.calcsize(PACK_HIST_LS) ),
        }
