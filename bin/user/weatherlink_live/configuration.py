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

import logging
from typing import List

from user.weatherlink_live.mappers import TMapping, THMapping, WindMapping, RainMapping, SolarMapping, UvMapping, \
    WindChillMapping, ThwMapping, ThswMapping, SoilTempMapping, SoilMoistureMapping, LeafWetnessMapping, \
    THIndoorMapping, BaroMapping, AbstractMapping
from user.weatherlink_live.static.config import KEY_DRIVER_POLLING_INTERVAL, KEY_DRIVER_HOST, KEY_DRIVER_MAPPING, \
    KEY_MAX_NO_DATA_ITERATIONS
from user.weatherlink_live.utils import to_list
from weeutil.weeutil import to_bool, to_float, to_int

MAPPERS = {
    't': TMapping,
    'th': THMapping,
    'wind': WindMapping,
    'rain': RainMapping,
    'solar': SolarMapping,
    'uv': UvMapping,
    'windchill': WindChillMapping,
    'thw': ThwMapping,
    'thsw': ThswMapping,
    'soil_temp': SoilTempMapping,
    'soil_moist': SoilMoistureMapping,
    'leaf_wet': LeafWetnessMapping,
    'th_indoor': THIndoorMapping,
    'baro': BaroMapping
}

log = logging.getLogger(__name__)


def create_configuration(config: dict, driver_name: str):
    """Create Configuration object from conf_dict"""

    driver_dict = config[driver_name]

    host = driver_dict[KEY_DRIVER_HOST]
    polling_interval = float(driver_dict.get(KEY_DRIVER_POLLING_INTERVAL, 10))
    max_no_data_iterations = to_int(driver_dict.get(KEY_MAX_NO_DATA_ITERATIONS, 5))
    mapping_list = to_list(driver_dict[KEY_DRIVER_MAPPING])
    mappings = _parse_mappings(mapping_list)

    log_success = to_bool(config.get('log_success', False))
    log_error = to_bool(config.get('log_failure', True))
    socket_timeout = to_float(config.get('socket_timeout', 20))

    config_obj = Configuration(
        host=host,
        mappings=mappings,
        polling_interval=polling_interval,
        max_no_data_iterations=max_no_data_iterations,
        log_success=log_success,
        log_error=log_error,
        socket_timeout=socket_timeout
    )
    return config_obj


def _parse_mappings(mappings_list: List[str]) -> List[List[str]]:
    mappings = [
        [mapping_opt.strip() for mapping_opt in mapping_opts.split(':')]
        for mapping_opts
        in mappings_list
    ]
    return mappings


class Configuration(object):
    """Configuration of driver"""

    def __init__(self,
                 host: str,
                 mappings: List[List[str]],
                 polling_interval: float,
                 max_no_data_iterations: int,
                 log_success: bool,
                 log_error: bool,
                 socket_timeout: float):
        self.host = host
        self.mappings = mappings
        self.polling_interval = polling_interval
        self.max_no_data_iterations = max_no_data_iterations

        self.log_success = log_success
        self.log_error = log_error
        self.socket_timeout = socket_timeout

    def __repr__(self):
        return str(self.__dict__)

    def create_mappers(self) -> List[AbstractMapping]:
        used_record_keys = []
        return [self._create_mapper(source_opts, used_record_keys) for source_opts in self.mappings]

    def _create_mapper(self, source_opts: List[str], used_map_targets: List[str]) -> AbstractMapping:
        type = source_opts[0]
        further_opts = source_opts[1:]

        log.debug("Creating mapper %s. Options: %s" % (type, further_opts))

        try:
            mapper_init = MAPPERS[type]
        except KeyError as e:
            raise KeyError("Unknown mapper type: %s" % repr(mapper_type)) from e

        mapper = mapper_init(further_opts, used_map_targets, self.log_success, self.log_error)
        return mapper
