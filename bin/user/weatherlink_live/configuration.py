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

import logging
from typing import List, Tuple, Iterable

from user.weatherlink_live.mappers import TMapping, THMapping, WindMapping, RainMapping, SolarMapping, UvMapping, \
    WindChillMapping, ThwMapping, ThswMapping, SoilTempMapping, SoilMoistureMapping, LeafWetnessMapping, \
    THIndoorMapping, BaroMapping, AbstractMapping, BatteryStatusMapping
from user.weatherlink_live.static import config as static_config, labels
from user.weatherlink_live.static.config import KEY_DRIVER_POLLING_INTERVAL, KEY_DRIVER_HOST, KEY_DRIVER_MAPPING, \
    KEY_MAX_NO_DATA_ITERATIONS
from user.weatherlink_live.utils import to_list
from weeutil.weeutil import to_bool, to_float, to_int

POLLING_INTERVAL_MIN = 10
POLLING_INTERVAL_DEFAULT = POLLING_INTERVAL_MIN
NO_DATA_ITERATIONS_DEFAULT = 5

MAPPERS = {
    static_config.KEY_MAPPER_TEMPERATURE_ONLY: TMapping,
    static_config.KEY_MAPPER_TEMPERATURE_HUMIDITY: THMapping,
    static_config.KEY_MAPPER_WIND: WindMapping,
    static_config.KEY_MAPPER_RAIN: RainMapping,
    static_config.KEY_MAPPER_SOLAR: SolarMapping,
    static_config.KEY_MAPPER_UV: UvMapping,
    static_config.KEY_MAPPER_WINDCHILL: WindChillMapping,
    static_config.KEY_MAPPER_THW: ThwMapping,
    static_config.KEY_MAPPER_THSW: ThswMapping,
    static_config.KEY_MAPPER_SOIL_TEMP: SoilTempMapping,
    static_config.KEY_MAPPER_SOIL_MOIST: SoilMoistureMapping,
    static_config.KEY_MAPPER_LEAF_WETNESS: LeafWetnessMapping,
    static_config.KEY_MAPPER_TH_INDOOR: THIndoorMapping,
    static_config.KEY_MAPPER_BARO: BaroMapping,
    static_config.KEY_MAPPER_BATTERY: BatteryStatusMapping,
}

log = logging.getLogger(__name__)


def create_configuration(config: dict, driver_name: str):
    """Create Configuration object from conf_dict"""

    driver_dict = config[driver_name]

    host = driver_dict[KEY_DRIVER_HOST]

    polling_interval = float(driver_dict.get(KEY_DRIVER_POLLING_INTERVAL, POLLING_INTERVAL_DEFAULT))
    if polling_interval < POLLING_INTERVAL_MIN:
        raise ValueError(
            "Polling interval has to be at least %d seconds (got: %d)" % (POLLING_INTERVAL_MIN, polling_interval))

    max_no_data_iterations = to_int(driver_dict.get(KEY_MAX_NO_DATA_ITERATIONS, NO_DATA_ITERATIONS_DEFAULT))
    if max_no_data_iterations < 1:
        raise ValueError("%s has to be at least 1" % KEY_MAX_NO_DATA_ITERATIONS)

    mapping_list = to_list(driver_dict.get(KEY_DRIVER_MAPPING, []))
    mappings = parse_mapping_definitions(mapping_list)

    sensors_section = driver_dict.get(static_config.KEY_SECTION_SENSORS, dict())
    sensor_definition_set = parse_sensor_definitions(sensors_section)

    log_success = to_bool(config.get(static_config.KEY_LOG_SUCCESS, False))
    log_success = to_bool(driver_dict.get(static_config.KEY_LOG_SUCCESS, log_success))

    log_error = to_bool(config.get(static_config.KEY_LOG_FAILURE, True))
    log_error = to_bool(driver_dict.get(static_config.KEY_LOG_FAILURE, log_error))

    socket_timeout = to_float(config.get('socket_timeout', 20))

    config_obj = Configuration(
        host=host,
        mappings=mappings,
        polling_interval=polling_interval,
        max_no_data_iterations=max_no_data_iterations,
        log_success=log_success,
        log_error=log_error,
        socket_timeout=socket_timeout,
        sensor_definition_set=sensor_definition_set,
    )
    return config_obj


MappingDefinition = List[str]
MappingDefinitionList = List[MappingDefinition]

SensorDefinition = Tuple[int, str, int | None]
SensorDefinitionSet = List[SensorDefinition]


def parse_sensor_definitions(sensors_section: dict) -> SensorDefinitionSet:
    definition_set = set()
    for transmitter_id in range(1, 8):
        sensor_key = str(transmitter_id)
        tx_sensor_list = to_list(sensors_section.get(sensor_key, []))

        new_definitions = _parse_tx_sensor_definitions(transmitter_id, tx_sensor_list)
        definition_set.update(new_definitions)

    return sorted(definition_set)


def _parse_tx_sensor_definitions(transmitter_id: int, tx_sensor_list: List[str]) -> SensorDefinitionSet:
    sensor_definitions: SensorDefinitionSet = list()

    for sensor_str in tx_sensor_list:
        clean_str = sensor_str.lower().strip()

        argument_count = clean_str.count(':')
        if argument_count < 1:
            sensor_def: SensorDefinition = (transmitter_id, clean_str, None)

        elif argument_count == 1:
            sensor_type, sensor_num_str = sensor_str.split(':', 2)

            try:
                sensor_num = int(sensor_num_str)
            except ValueError as e:
                raise ValueError("Failed to parse sensor number in sensor definition: %s" % repr(sensor_num_str)) from e

            sensor_def: SensorDefinition = (transmitter_id, sensor_type, sensor_num)

        else:
            raise ValueError(
                "Invalid number of arguments (%d) for sensor definition: %s" % (argument_count, sensor_str))

        sensor_definitions.append(sensor_def)

    return sensor_definitions


def build_sensor_definitions(sensor_config: Iterable[SensorDefinition]) -> dict[str, list[str]]:
    sensor_section: dict[str, list[str]] = dict()

    for tx_id, sensor_type, sensor_number in sensor_config:
        tx_id_str = str(tx_id)
        if tx_id_str not in sensor_section:
            sensor_section[tx_id_str] = list()

        if sensor_number is None:
            sensor_section[tx_id_str].append(sensor_type)
        else:
            sensor_section[tx_id_str].append("%s:%d" % (sensor_type, sensor_number))

    return sensor_section


def build_sensor_definition_comments(sensor_config: Iterable[SensorDefinition]) -> dict[str, list[str]]:
    sensor_section: dict[str, list[str]] = dict()

    for tx_id, sensor_type, sensor_number in sensor_config:
        tx_id_str = str(tx_id)
        if tx_id_str not in sensor_section:
            sensor_section[tx_id_str] = ["", "Transmitter %d:" % tx_id]

        sensor_label = labels.SENSOR_LABELS[sensor_type]
        if sensor_number is None:
            sensor_section[tx_id_str].append(" - %s" % sensor_label)
        else:
            sensor_section[tx_id_str].append(" - %s | %d" % (sensor_label, sensor_number))

    return sensor_section


def parse_mapping_definitions(mappings_list: List[str]) -> MappingDefinitionList:
    return [
        [mapping_opt.strip() for mapping_opt in mapping_opts.split(':')]
        for mapping_opts
        in mappings_list
    ]


def build_mapping_definitions(mapping_definitions: MappingDefinitionList) -> List[str]:
    return [":".join(definition) for definition in mapping_definitions]


def create_mappers(mapping_definitions: MappingDefinitionList, log_success: bool, log_error: bool) -> List[
    AbstractMapping]:
    used_record_keys = []
    mappers = []
    for source_opts in mapping_definitions:
        mapper = _create_mapper(source_opts, used_record_keys, log_success, log_error)
        mappers.append(mapper)
        used_record_keys.extend(mapper.targets.values())
    return mappers


def _create_mapper(source_opts: List[str],
                   used_map_targets: List[str],
                   log_success: bool,
                   log_error: bool) -> AbstractMapping:
    mapper_type = source_opts[0]
    further_opts = source_opts[1:]

    log.debug("Creating mapper %s. Options: %s" % (mapper_type, further_opts))

    try:
        mapper_init = MAPPERS[mapper_type]
    except KeyError as e:
        raise KeyError("Unknown mapper type: %s" % repr(mapper_type)) from e

    mapper = mapper_init(further_opts, used_map_targets, log_success, log_error)
    return mapper


class Configuration(object):
    """Configuration of driver"""

    def __init__(self,
                 host: str,
                 mappings: MappingDefinitionList,
                 polling_interval: float,
                 max_no_data_iterations: int,
                 log_success: bool,
                 log_error: bool,
                 socket_timeout: float,
                 sensor_definition_set: SensorDefinitionSet | None = None):
        self.host = host
        self.mappings = mappings
        self.polling_interval = polling_interval
        self.max_no_data_iterations = max_no_data_iterations

        if sensor_definition_set is not None:
            self.sensor_definition_set = sensor_definition_set
        else:
            self.sensor_definition_set = list()

        self.log_success = log_success
        self.log_error = log_error
        self.socket_timeout = socket_timeout

    def __repr__(self):
        return str(self.__dict__)

    def create_mappers(self) -> List[AbstractMapping]:
        return create_mappers(self.mappings, self.log_success, self.log_error)

    @property
    def has_mappings(self) -> bool:
        return len(self.mappings) > 0

    @property
    def has_sensors(self) -> bool:
        return len(self.sensor_definition_set) > 0
