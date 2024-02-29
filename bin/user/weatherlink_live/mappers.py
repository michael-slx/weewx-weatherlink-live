# Copyright © 2020-2024 Michael Schantl and contributors
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
from typing import Dict, List, Optional, Union

from user.weatherlink_live.packets import NotInPacket, DavisConditionsPacket
from user.weatherlink_live.static import PacketSource, targets, labels
from user.weatherlink_live.static.packets import DataStructureType, KEY_TEMPERATURE, KEY_HUMIDITY, KEY_DEW_POINT, \
    KEY_HEAT_INDEX, KEY_WET_BULB, KEY_WIND_DIR, KEY_RAIN_AMOUNT_DAILY, KEY_RAIN_SIZE, KEY_RAIN_RATE, \
    KEY_SOLAR_RADIATION, KEY_UV_INDEX, KEY_WIND_CHILL, KEY_THW_INDEX, KEY_THSW_INDEX, KEY_SOIL_MOISTURE, \
    KEY_TEMPERATURE_LEAF_SOIL, KEY_LEAF_WETNESS, KEY_TEMPERATURE_INDOOR, KEY_HUMIDITY_INDOOR, KEY_DEW_POINT_INDOOR, \
    KEY_HEAT_INDEX_INDOOR, KEY_BARO_ABSOLUTE, KEY_BARO_SEA_LEVEL, KEY_WIND_SPEED, KEY_BATTERY_FLAG, \
    KEY_WLL_BATTERY, KEY_WLL_SUPPLY, KEY_GUST_SPEED, KEY_GUST_DIR, KEY_RAIN_AMOUNT

log = logging.getLogger(__name__)


def _parse_option_boolean(opts: list, check_for: str) -> bool:
    if len(opts) < 1:
        return False

    uppercase_opts = [opt.upper() for opt in opts]
    uppercase_check_for = check_for.upper()

    return uppercase_check_for in uppercase_opts


class AbstractMapping(object):
    def __init__(self, mapping_opts: list, used_map_targets: list,
                 log_success: bool = False, log_error: bool = True):
        self.mapping_opts = mapping_opts

        self.log_success = log_success
        self.log_error = log_error

        self.targets = self.__search_multi_targets(self._map_target_dict, used_map_targets)
        self._log_success("Mapping targets: %s" % repr(self.targets))

    def __str__(self):
        return type(self).__name__ + (repr(self.mapping_opts) if self.mapping_opts else "")

    def _log_success(self, message: str, level: int = logging.DEBUG) -> None:
        if self.log_success:
            log.log(level, "%s: %s" % (str(self), message))

    def _log_error(self, message: str, level: int = logging.DEBUG) -> None:
        if self.log_error:
            log.log(level, "%s: %s" % (str(self), message))

    def _log_mapping_success(self, target: str, value: float = None):
        self._log_success("Mapped: %s=%s" % (target, repr(value)))

    def _log_mapping_notResponsible(self, message: str):
        """Logged when the mapper doesn't feel responsible for a packet"""
        self._log_success("Mapping not responsible: %s" % message)

    def _log_mapping_notInPacket(self):
        self._log_success("Observation not found in packet")

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

    def __search_multi_targets(self, available_map_targets_dict: dict = (), used_map_targets=None) -> dict:
        if used_map_targets is None:
            used_map_targets = []

        if len(available_map_targets_dict) < 1:
            return {}

        target_length = min([len(target_list) for target_list in available_map_targets_dict.values()])
        for i in range(0, target_length):
            map_targets = dict([
                (k, v[i]) for k, v in available_map_targets_dict.items()
            ])

            if any([map_target in used_map_targets for map_target in map_targets.values()]):
                continue
            else:
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

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        raise NotImplementedError()

    def _set_record_entry(self, record: dict, key: str, value: float = None):
        record.update({key: value})
        self._log_mapping_success(key, value)

    @property
    def map_source_transmitter(self) -> str:
        raise NotImplementedError()

    @property
    def map_table(self) -> Dict[str, Union[str, list[str]]]:
        raise NotImplementedError()


class TMapping(AbstractMapping):

    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            't': targets.TEMP
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['t']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_TEMPERATURE, DataStructureType.ISS, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_TEMPERATURE: self.targets['t'],
        }


class THMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            't': targets.TEMP,
            'h': targets.HUM,
            'dp': targets.DEW_POINT,
            'hi': targets.HEAT_INDEX,
            'wb': targets.WET_BULB
        }

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

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_TEMPERATURE: self.targets['t'],
            labels.LABEL_HUMIDITY: self.targets['h'],
            labels.LABEL_DEW_POINT: self.targets['dp'],
            labels.LABEL_HEAT_INDEX: self.targets['hi'],
            labels.LABEL_WET_BULB: self.targets['wb'],
        }


class WindMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'wind_dir': targets.WIND_DIR,
            'wind_speed': targets.WIND_SPEED,
            'gust_dir': targets.WIND_GUST_DIR,
            'gust_speed': targets.WIND_GUST_SPEED
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        if packet.data_source not in [ PacketSource.WEATHER_PUSH, PacketSource.WEATHER_WLCOM ]: 
            self._log_mapping_notResponsible("Not a broadcast packet")
            return

        target_dir = self.targets['wind_dir']
        target_speed = self.targets['wind_speed']

        self._set_record_entry(record, target_dir,
                               packet.get_observation(KEY_WIND_DIR, DataStructureType.ISS, self.tx_id))
        self._set_record_entry(record, target_speed,
                               packet.get_observation(KEY_WIND_SPEED, DataStructureType.ISS, self.tx_id))

        if packet.data_source == PacketSource.WEATHER_WLCOM:
            target_gust_dir = self.targets['gust_dir']
            target_gust_speed = self.targets['gust_speed']

            self._set_record_entry(record, target_gust_dir,
                                   packet.get_observation(KEY_GUST_DIR, DataStructureType.ISS, self.tx_id))
            self._set_record_entry(record, target_gust_speed,
                                   packet.get_observation(KEY_GUST_SPEED, DataStructureType.ISS, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_WIND_SPEED: self.targets['wind_speed'],
            labels.LABEL_WIND_DIR: self.targets['wind_dir'],
            labels.LABEL_WIND_GUST_SPEED: self.targets['gust_speed'],
            labels.LABEL_WIND_GUST_DIR: self.targets['gust_dir'],
        }


class RainMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        # 0: Reserved, 1: 0.01", 2: 0.2 mm, 3:  0.1 mm, 4: 0.001"
        self.rain_bucket_sizes = {
            1: 0.01,
            4: 0.001,
            2: (1 / 25.4) * 0.2,
            3: (1 / 25.4) * 0.1
        }

        self.tx_id = self._parse_option_int(mapping_opts, 0)

        self.last_daily_rain_count = None

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'amount': targets.RAIN_AMOUNT,
            'rate': targets.RAIN_RATE,
            'count': targets.RAIN_COUNT,
            'count_rate': targets.RAIN_COUNT_RATE,
            'size': targets.RAIN_SIZE,
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        if packet.data_source not in [ PacketSource.WEATHER_PUSH, PacketSource.WEATHER_WLCOM ]:
            self._log_mapping_notResponsible("Not a broadcast or archive packet")
            return

        target_amount = self.targets['amount']
        target_rate = self.targets['rate']
        target_count = self.targets['count']
        target_rate_count = self.targets['count_rate']
        target_size = self.targets['size']

        rain_bucket_factor = self.rain_bucket_factor(packet)
        self._set_record_entry(record, target_size, rain_bucket_factor)

        if packet.data_source == PacketSource.WEATHER_WLCOM:
            rain_count = packet.get_observation(KEY_RAIN_AMOUNT, DataStructureType.ISS, self.tx_id)
            self._set_record_entry(record, target_count, rain_count)
            self._set_record_entry(record, target_amount, self._multiply(rain_count, rain_bucket_factor))
            return
            
        rain_rate_count = packet.get_observation(KEY_RAIN_RATE, DataStructureType.ISS, self.tx_id)
        self._set_record_entry(record, target_rate_count, rain_rate_count)
        self._set_record_entry(record, target_rate, self._multiply(rain_rate_count, rain_bucket_factor))

        current_daily_rain_count = packet.get_observation(KEY_RAIN_AMOUNT_DAILY, DataStructureType.ISS, self.tx_id)
        if current_daily_rain_count is None:
            self._log_error("Daily rain count not in packet. Skipping diff calculation")
            return

        if self.last_daily_rain_count is None:
            self._log_success("First daily rain value", logging.INFO)

        elif self.last_daily_rain_count > current_daily_rain_count:
            self._log_success("Last daily rain (%d) larger than current (%d). Probably reset" % (
                self.last_daily_rain_count, current_daily_rain_count), logging.INFO)
            self._set_record_entry(record, target_count, current_daily_rain_count)
            self._set_record_entry(record, target_amount, self._multiply(current_daily_rain_count, rain_bucket_factor))

        else:
            count_diff = current_daily_rain_count - self.last_daily_rain_count
            self._set_record_entry(record, target_count, count_diff)
            self._set_record_entry(record, target_amount, self._multiply(count_diff, rain_bucket_factor))

        self.last_daily_rain_count = current_daily_rain_count

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

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
            raise KeyError("Unexpected rain bucket size %s" % repr(rain_bucket_size)) from e

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_RAIN_AMOUNT: self.targets['amount'],
            labels.LABEL_RAIN_RATE: self.targets['rate'],
            labels.LABEL_RAIN_COUNT: self.targets['count'],
            labels.LABEL_RAIN_COUNT_RATE: self.targets['count_rate'],
            labels.LABEL_RAIN_SIZE: self.targets['size'],
        }


class SolarMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'solar': targets.SOLAR_RADIATION
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['solar']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_SOLAR_RADIATION, DataStructureType.ISS, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_SOLAR_RADIATION: self.targets['solar'],
        }


class UvMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'uv': targets.UV
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['uv']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_UV_INDEX, DataStructureType.ISS, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_UV_INDEX: self.targets['uv'],
        }


class WindChillMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'windchill': targets.WINDCHILL
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['windchill']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_WIND_CHILL, DataStructureType.ISS, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_WIND_CHILL: self.targets['windchill'],
        }


class ThwMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        self.is_app_temp = _parse_option_boolean(mapping_opts, 'appTemp')

        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        target_dict = {
            'thw': targets.THW,
            'app_temp': targets.APPARENT_TEMPERATURE
        } if self.is_app_temp else {
            'thw': targets.THW
        }
        return target_dict

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['thw']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_THW_INDEX, DataStructureType.ISS, self.tx_id))

        if self.is_app_temp:
            target_app_temp = self.targets['app_temp']
            self._set_record_entry(record, target_app_temp,
                                   packet.get_observation(KEY_THW_INDEX, DataStructureType.ISS, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, list[str]]:
        return {
            labels.LABEL_THW_INDEX: [self.targets['thw'], self.targets['app_temp']] if self.is_app_temp else [
                self.targets['thw']],
        }


class ThswMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        self.is_app_temp = _parse_option_boolean(mapping_opts, 'appTemp')

        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        target_dict = {
            'thsw': targets.THSW,
            'app_temp': targets.APPARENT_TEMPERATURE
        } if self.is_app_temp else {
            'thsw': targets.THSW
        }
        return target_dict

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['thsw']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_THSW_INDEX, DataStructureType.ISS, self.tx_id))

        if self.is_app_temp:
            target_app_temp = self.targets['app_temp']
            self._set_record_entry(record, target_app_temp,
                                   packet.get_observation(KEY_THSW_INDEX, DataStructureType.ISS, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, list[str]]:
        return {
            labels.LABEL_THSW_INDEX: [self.targets['thsw'], self.targets['app_temp']] if self.is_app_temp else [
                self.targets['thsw']],
        }


class SoilTempMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)
        self.sensor = self._parse_option_int(mapping_opts, 1)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'soil_temp': targets.SOIL_TEMP
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['soil_temp']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_TEMPERATURE_LEAF_SOIL % self.sensor,
                                                      DataStructureType.LEAF_SOIL, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            (labels.LABEL_SOIL_TEMPERATURE % self.sensor): self.targets['soil_temp'],
        }


class SoilMoistureMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)
        self.sensor = self._parse_option_int(mapping_opts, 1)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'soil_moisture': targets.SOIL_MOISTURE
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['soil_moisture']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_SOIL_MOISTURE % self.sensor,
                                                      DataStructureType.LEAF_SOIL, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            (labels.LABEL_SOIL_MOISTURE % self.sensor): self.targets['soil_moisture'],
        }


class LeafWetnessMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)
        self.sensor = self._parse_option_int(mapping_opts, 1)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'leaf_wetness': targets.LEAF_WETNESS
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target = self.targets['leaf_wetness']

        self._set_record_entry(record, target,
                               packet.get_observation(KEY_LEAF_WETNESS % self.sensor,
                                                      DataStructureType.LEAF_SOIL, self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            (labels.LABEL_LEAF_WETNESS % self.sensor): self.targets['leaf_wetness'],
        }


class THIndoorMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            't': targets.INDOOR_TEMP,
            'h': targets.INDOOR_HUM,
            'dp': targets.INDOOR_DEW_POINT,
            'hi': targets.INDOOR_HEAT_INDEX
        }

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

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_WLL_TH

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_TEMPERATURE_INDOOR: self.targets['t'],
            labels.LABEL_HUMIDITY_INDOOR: self.targets['h'],
            labels.LABEL_DEW_POINT_INDOOR: self.targets['dp'],
            labels.LABEL_HEAT_INDEX_INDOOR: self.targets['hi'],
        }


class BaroMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'baro_abs': targets.BARO_ABSOLUTE,
            'baro_sl': targets.BARO_SEA_LEVEL
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        target_abs = self.targets['baro_abs']
        target_sl = self.targets['baro_sl']

        self._set_record_entry(record, target_abs,
                               packet.get_observation(KEY_BARO_ABSOLUTE, DataStructureType.WLL_BARO))
        self._set_record_entry(record, target_sl,
                               packet.get_observation(KEY_BARO_SEA_LEVEL, DataStructureType.WLL_BARO))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_WLL_BAROMETER

    @property
    def map_table(self) -> Dict[str, str]:
        return {
            labels.LABEL_BARO_ABSOLUTE: self.targets['baro_abs'],
            labels.LABEL_BARO_SEA_LEVEL: self.targets['baro_sl'],
        }


class BatteryStatusMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

        further_opts = mapping_opts[1:]
        try:
            self.further_targets = [targets.BATTERY_STATUS_NAMED[key] for key in further_opts]
        except KeyError as e:
            raise KeyError("Invalid battery remap target") from e

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'battery': targets.BATTERY_STATUS
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        battery_num = self.targets['battery']

        self._set_record_entry(record, battery_num,
                               packet.get_observation(KEY_BATTERY_FLAG, tx=self.tx_id))
        for target in self.further_targets:
            self._set_record_entry(record, target,
                                   packet.get_observation(KEY_BATTERY_FLAG, tx=self.tx_id))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, list[str]]:
            labels.LABEL_BATTERY_STATUS: [self.targets['battery'], *self.further_targets]


class VoltageMapping(AbstractMapping):
    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return {
            'voltage': list(targets.VOLTAGE_NAMED.values()),
            'batt': targets.VOLTAGE_WLL_BATT,
            'supply': targets.VOLTAGE_WLL_SUPPLY
        }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        for obs, target in targets.VOLTAGE_NAMED.items():
            self._set_record_entry(record, target, packet.get_observation(obs, tx=self.tx_id))

        for conditions in packet._conditions:
            if conditions.get('data_structure_type') == DataStructureType.WLL_HEALTH:
                target_b = self.targets['batt']
                target_s = self.targets['supply']

                self._set_record_entry(record, target_b,
                                       packet.get_observation(KEY_WLL_BATTERY, DataStructureType.WLL_HEALTH))
                self._set_record_entry(record, target_s,
                                       packet.get_observation(KEY_WLL_SUPPLY, DataStructureType.WLL_HEALTH))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, list[str]]:
        return {
            labels.LABEL_VOLTAGE: self.targets['voltage'],
            labels.LABEL_WLL_BATTERY: self.targets['batt'],
            labels.LABEL_WLL_SUPPLY: self.targets['supply'],
        }


class CommMapping(AbstractMapping):

    def __init__(self, mapping_opts: list, used_map_targets: list, log_success: bool = False, log_error: bool = True):
        super().__init__(mapping_opts, used_map_targets, log_success, log_error)

        self.tx_id = self._parse_option_int(mapping_opts, 0)
        self.wll_dict = {
            'uptime': 'uptime',
            'rx_bytes': 'rxBytes',
            'tx_bytes': 'txBytes',
            'local_api_queries': 'localApiQueries',
            'rapid_records_sent': 'rapidRecordsSent',
            'wifi_rssi': 'wifiRssi',
            'link_uptime': 'linkUptime',
            'network_error': 'networkError',
            'touchpad_wakeups': 'touchpadWakeups',
        }
        self.iss_dict = {
            'reception': 'reception',
            'rssi': 'rssi',
            'error_packets': 'errorPackets',
            'resynchs': 'resyncs',
            'good_packets_streak': 'goodPacketsStreaks'
        }

    @property
    def _map_target_dict(self) -> Dict[str, List[str]]:
        return { }

    def _do_mapping(self, packet: DavisConditionsPacket, record: dict):
        for obs, target in self.iss_dict.items():
            self._set_record_entry(record, target, packet.get_observation(obs, tx=self.tx_id))

        for conditions in packet._conditions:
            if conditions.get('data_structure_type') == DataStructureType.WLL_HEALTH:
                for obs, target in self.wll_dict.items():
                    self._set_record_entry(record, target,
                                       packet.get_observation(obs, DataStructureType.WLL_HEALTH))

    @property
    def map_source_transmitter(self) -> str:
        return labels.LABEL_SOURCE_TX_ID % self.tx_id

    @property
    def map_table(self) -> Dict[str, list[str]]:
        return {
            labels.LABEL_WLL_UPTIME: self.targets['uptime'],
            labels.LABEL_WLL_RX_BYTES: self.targets['rx_bytes'],
            labels.LABEL_WLL_TX_BYTES: self.targets['tx_bytes'],
            labels.LABEL_WLL_LOCAL_API: self.targets['local_api_queries'],
            labels.LABEL_WLL_RAPID_RECORDS: self.targets['rapid_records_sent'],
            labels.LABEL_WLL_WIFI_RSSI: self.targets['wifi_rssi'],
            labels.LABEL_WLL_LINK_UPTIME: self.targets['link_uptime'],
            labels.LABEL_WLL_NET_ERROR: self.targets['network_error'],
            labels.LABEL_WLL_TOUCHPAD: self.targets['touchpad_wakeups'],
            labels.LABEL_WLL_RECEPTION: self.targets['reception'],
            labels.LABEL_WLL_RSSI: self.targets['rssi'],
            labels.LABEL_WLL_ERROR_PACKETS: self.targets['error_packets'],
            labels.LABEL_WLL_RESYNCHS: self.targets['resynchs'],
            labels.LABEL_WLL_GOOD_STREAK: self.targets['good_packets_streak']
        }
