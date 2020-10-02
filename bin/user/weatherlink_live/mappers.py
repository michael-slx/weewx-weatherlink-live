# Copyright © 2020 Michael Schantl and contributors
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
Mappings of API to observations
"""
import logging
from typing import Dict, List, Optional

from user.weatherlink_live.packets import NotInPacket, DavisConditionsPacket
from user.weatherlink_live.static import PacketSource, targets
from user.weatherlink_live.static.packets import DataStructureType, KEY_TEMPERATURE, KEY_HUMIDITY, KEY_DEW_POINT, \
    KEY_HEAT_INDEX, KEY_WET_BULB, KEY_WIND_DIR, KEY_RAIN_AMOUNT_DAILY, KEY_RAIN_SIZE, KEY_RAIN_RATE, \
    KEY_SOLAR_RADIATION, KEY_UV_INDEX, KEY_WIND_CHILL, KEY_THW_INDEX, KEY_THSW_INDEX, KEY_SOIL_MOISTURE, \
    KEY_TEMPERATURE_LEAF_SOIL, KEY_LEAF_WETNESS, KEY_TEMPERATURE_INDOOR, KEY_HUMIDITY_INDOOR, KEY_DEW_POINT_INDOOR, \
    KEY_HEAT_INDEX_INDOOR, KEY_BARO_ABSOLUTE, KEY_BARO_SEA_LEVEL, KEY_WIND_SPEED

log = logging.getLogger(__name__)


class AbstractMapping(object):
    def __init__(self, mapping_targets: Dict[str, List[str]], mapping_opts: list, used_map_targets: list,
                 log_success: bool = False, log_error: bool = True):
        self.mapping_opts = mapping_opts

        self.log_success = log_success
        self.log_error = log_error

        self.targets = self.__search_multi_targets(mapping_targets, used_map_targets)
        self._log("Mapping targets: %s" % repr(self.targets))

    def __str__(self):
        return "%s[%s]" % (type(self).__name__, self.mapping_opts)

    def _log(self, message: str, level: int = logging.DEBUG):
        log.log(level, "%s: %s" % (str(self), message))

    def _log_mapping_success(self, target: str, value: float = None):
        if self.log_success:
            self._log("Mapped: %s=%s" % (target, repr(value)))

    def _log_mapping_notResponsible(self, message: str):
        """Logged when the mapper doesn't feel responsible for a packet"""
        if self.log_success:  # because this is part of normal operation
            self._log("Mapping not responsible: %s" % message)

    def _log_mapping_notInPacket(self):
        if self.log_success: # not an error
            self._log("Mapping failure: Observation not found in packet")

    def _parse_option_int(self, opts: list, index: int) -> int:
        try:
            return int(opts[index])
        except IndexError as e:
            raise IndexError("Mapping options for mapping %s incomplete: Expected at least %d parameters; got %d" % (
                str(self), index + 1, len(opts)
            )) from e
        except ValueError as e:
            raise ValueError("Could not parse mapping option %d for mapping %s: Expected an integer; got %s" % (
                index + 1, str(self), repr(opts[index])
            )) from e

    def __search_multi_targets(self, available_map_targets_dict: dict = (), used_map_targets: list = []) -> dict:
        max_idx = min([len(l)
                       for l in available_map_targets_dict.values()]) - 1

        for i in range(0, max_idx + 1):
            map_targets = dict([(k, v[i])
                                for k, v
                                in available_map_targets_dict.items()])
            if any([map_target in used_map_targets for map_target in map_targets.values()]):
                continue

            return map_targets

        raise RuntimeError("Mapping %s has all map targets used: %s" % (
            str(self), available_map_targets_dict
        ))

    def map(self, packet: DavisConditionsPacket, record: dict):
        try:
            self._do_mapping(packet, record)
        except NotInPacket:
            self._log_mapping_notInPacket()
            pass

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        pass

    def _set_record_entry(self, record: dict, key: str, value: float = None):
        record.update({key: value})
        self._log_mapping_success(key, value)


class TMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            't': targets.TEMP
        }, mapping_opts, used_map_targets, log_success, log_error)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['t']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_TEMPERATURE, DataStructureType.ISS, self.tx))


class THMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            't': targets.TEMP,
            'h': targets.HUM,
            'dp': targets.DEW_POINT,
            'hi': targets.HEAT_INDEX,
            'wb': targets.WET_BULB
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target_t = self.targets['t']
        target_h = self.targets['h']
        target_dp = self.targets['dp']
        target_hi = self.targets['hi']
        target_wb = self.targets['wb']

        self._set_record_entry(record, target_t,
                               packet.get_observation(KEY_TEMPERATURE, DataStructureType.ISS, self.tx_id))
        self._set_record_entry(record, target_h,
                               packet.get_observation(KEY_HUMIDITY, DataStructureType.ISS, self.tx_id))
        self._set_record_entry(record, target_dp,
                               packet.get_observation(KEY_DEW_POINT, DataStructureType.ISS, self.tx_id))
        self._set_record_entry(record, target_hi,
                               packet.get_observation(KEY_HEAT_INDEX, DataStructureType.ISS, self.tx_id))
        self._set_record_entry(record, target_wb,
                               packet.get_observation(KEY_WET_BULB, DataStructureType.ISS, self.tx_id))


class WindMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'wind_dir': targets.WIND_DIR,
            'wind_speed': targets.WIND_SPEED,
            'gust_dir': targets.WIND_GUST_DIR,
            'gust_speed': targets.WIND_GUST_SPEED
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        if packet.data_source != PacketSource.WEATHER_PUSH:
            self._log_mapping_notResponsible("Not a broadcast packet")
            return

        target_dir = self.targets['wind_dir']
        target_speed = self.targets['wind_speed']

        self._set_record_entry(record, target_dir,
                               packet.get_observation(KEY_WIND_DIR, DataStructureType.ISS, self.tx_id))
        self._set_record_entry(record, target_speed,
                               packet.get_observation(KEY_WIND_SPEED, DataStructureType.ISS, self.tx_id))


class RainMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'amount': targets.RAIN_AMOUNT,
            'rate': targets.RAIN_RATE,
            'count': targets.RAIN_COUNT,
            'count_rate': targets.RAIN_COUNT_RATE,
            'size': targets.RAIN_SIZE,
        }, mapping_opts, used_map_targets, log_success, log_error)

        # 0: Reserved, 1: 0.01", 2: 0.2 mm, 3:  0.1 mm, 4: 0.001"
        self.rain_bucket_sizes = {
            1: 0.01,
            4: 0.001,
            2: (1 / 25.4) * 0.2,
            3: (1 / 25.4) * 0.1
        }

        self.tx_id = self._parse_option_int(mapping_opts, 0)

        self.last_daily_rain_count = None

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        if packet.data_source != PacketSource.WEATHER_PUSH:
            self._log_mapping_notResponsible("Not a broadcast packet")
            return

        target_amount = self.targets['amount']
        target_rate = self.targets['rate']
        target_count = self.targets['count']
        target_rate_count = self.targets['count_rate']
        target_size = self.targets['size']

        rain_bucket_factor = self.rain_bucket_factor(packet)
        self._set_record_entry(record, target_size, rain_bucket_factor)

        rain_rate_count = packet.get_observation(KEY_RAIN_RATE, DataStructureType.ISS, self.tx_id)
        self._set_record_entry(record, target_rate_count, rain_rate_count)
        self._set_record_entry(record, target_rate, self._multiply(rain_rate_count, rain_bucket_factor))

        current_daily_rain_count = packet.get_observation(KEY_RAIN_AMOUNT_DAILY, DataStructureType.ISS, self.tx_id)
        if current_daily_rain_count is None:
            self._log("Daily rain count not in packet. Skipping diff calculation")
            return

        if self.last_daily_rain_count is None:
            self._log("First daily rain value", logging.INFO)

        elif self.last_daily_rain_count > current_daily_rain_count:
            self._log("Last daily rain (%d) larger than current (%d). Probably reset" % (
                self.last_daily_rain_count, current_daily_rain_count), logging.INFO)
            self._set_record_entry(record, target_count, current_daily_rain_count)
            self._set_record_entry(record, target_amount, self._multiply(current_daily_rain_count, rain_bucket_factor))

        else:
            count_diff = self.last_daily_rain_count - current_daily_rain_count
            self._set_record_entry(record, target_count, count_diff)
            self._set_record_entry(record, target_amount, self._multiply(count_diff, rain_bucket_factor))

        self.last_daily_rain_count = current_daily_rain_count

    @staticmethod
    def _multiply(a: Optional[float], b: Optional[float]) -> Optional[float]:
        if a is None or b is None:
            return None
        return a * b

    def rain_bucket_factor(self, packet) -> Optional[float]:
        rain_bucket_size = packet.get_observation(KEY_RAIN_SIZE, DataStructureType.ISS, self.tx_id)
        if rain_bucket_size is None:
            return None

        try:
            return self.rain_bucket_sizes[rain_bucket_size]
        except KeyError as e:
            raise KeyError("Unexpected rain bucket size %s" % repr(rain_bucket_size))


class SolarMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'solar': targets.SOLAR_RADIATION
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['solar']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_SOLAR_RADIATION, DataStructureType.ISS, self.tx_id))



class UvMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'uv': targets.UV
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['uv']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_UV_INDEX, DataStructureType.ISS, self.tx_id))


class WindChillMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'windchill': targets.WINDCHILL
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['windchill']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_WIND_CHILL, DataStructureType.ISS, self.tx_id))


class ThwMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'thw': targets.THW
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['thw']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_THW_INDEX, DataStructureType.ISS, self.tx_id))


class ThswMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'thsw': targets.THSW
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['thsw']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_THSW_INDEX, DataStructureType.ISS, self.tx_id))


class SoilTempMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'soil_temp': targets.SOIL_TEMP
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)
        self.sensor = self._parse_option_int(mapping_opts, 1)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['soil_temp']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_TEMPERATURE_LEAF_SOIL % self.sensor,
                                                      DataStructureType.LEAF_SOIL, self.tx_id))


class SoilMoistureMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'soil_moisture': targets.SOIL_MOISTURE
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)
        self.sensor = self._parse_option_int(mapping_opts, 1)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['soil_moisture']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_SOIL_MOISTURE % self.sensor,
                                                      DataStructureType.LEAF_SOIL, self.tx_id))


class LeafWetnessMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'leaf_wetness': targets.LEAF_WETNESS
        }, mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)
        self.sensor = self._parse_option_int(mapping_opts, 1)


    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['leaf_wetness']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_LEAF_WETNESS % self.sensor,
                                                      DataStructureType.LEAF_SOIL, self.tx_id))


class THIndoorMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            't': targets.INDOOR_TEMP,
            'h': targets.INDOOR_HUM,
            'dp': targets.INDOOR_DEW_POINT,
            'hi': targets.INDOOR_HEAT_INDEX
        }, mapping_opts, used_map_targets, log_success, log_error)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target_t = self.targets['t']
        target_h = self.targets['h']
        target_dp = self.targets['dp']
        target_hi = self.targets['hi']

        self._set_record_entry(record, target_t,
                               packet.get_observation(KEY_TEMPERATURE_INDOOR, DataStructureType.WLL_TH))
        self._set_record_entry(record, target_h,
                               packet.get_observation(KEY_HUMIDITY_INDOOR, DataStructureType.WLL_TH))
        self._set_record_entry(record, target_dp,
                               packet.get_observation(KEY_DEW_POINT_INDOOR, DataStructureType.WLL_TH))
        self._set_record_entry(record, target_hi,
                               packet.get_observation(KEY_HEAT_INDEX_INDOOR, DataStructureType.WLL_TH))


class BaroMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__({
            'baro_abs': targets.BARO_ABSOLUTE,
            'baro_sl': targets.BARO_SEA_LEVEL
        }, mapping_opts, used_map_targets, log_success, log_error)

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target_abs = self.targets['baro_abs']
        target_sl = self.targets['baro_sl']

        self._set_record_entry(record, target_abs,
                               packet.get_observation(KEY_BARO_ABSOLUTE, DataStructureType.WLL_BARO))
        self._set_record_entry(record, target_sl,
                               packet.get_observation(KEY_BARO_SEA_LEVEL, DataStructureType.WLL_BARO))
