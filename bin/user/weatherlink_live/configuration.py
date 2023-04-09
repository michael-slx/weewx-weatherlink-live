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
from typing import List

from user.weatherlink_live.mappers import TMapping, THMapping, WindMapping, RainMapping, SolarMapping, UvMapping, \
    WindChillMapping, ThwMapping, ThswMapping, SoilTempMapping, SoilMoistureMapping, LeafWetnessMapping, \
    THIndoorMapping, BaroMapping, AbstractMapping, BatteryStatusMapping, VoltageMapping, CommMapping
from user.weatherlink_live.static import config as static_config
from user.weatherlink_live.static.config import KEY_DRIVER_POLLING_INTERVAL, KEY_DRIVER_HOST, KEY_DRIVER_MAPPING, \
    KEY_MAX_NO_DATA_ITERATIONS, KEY_DRIVER_WLCOM
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
    static_config.KEY_MAPPER_VOLTAGE: VoltageMapping,
    static_config.KEY_MAPPER_COMM: CommMapping
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

    use_wlcom = to_bool(driver_dict.get(KEY_DRIVER_WLCOM, False))

    mapping_list = to_list(driver_dict[KEY_DRIVER_MAPPING])
    mappings = parse_mapping_definitions(mapping_list)
    if len(mappings) < 1:
        raise ValueError("At least 1 mapping has to be defined")

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
        use_wlcom=use_wlcom,
        socket_timeout=socket_timeout
    )
    return config_obj


MappingDefinition = List[str]
MappingDefinitionList = List[MappingDefinition]


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
                 use_wlcom: bool,
                 socket_timeout: float):
        self.host = host
        self.mappings = mappings
        self.polling_interval = polling_interval
        self.max_no_data_iterations = max_no_data_iterations
        self.use_wlcom = use_wlcom

        self.log_success = log_success
        self.log_error = log_error
        self.socket_timeout = socket_timeout

    def __repr__(self):
        return str(self.__dict__)

    def create_mappers(self) -> List[AbstractMapping]:
        return create_mappers(self.mappings, self.log_success, self.log_error)
