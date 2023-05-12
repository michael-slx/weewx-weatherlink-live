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
from typing import List, Set, Iterable

from user.weatherlink_live import configuration, mappers
from user.weatherlink_live.static import config as config_static

logger = logging.getLogger(__name__)


def create_mappers_from_sensors(sensors: configuration.SensorDefinitionMap,
                                config: configuration.Configuration) -> List[mappers.AbstractMapping]:
    mapper_list = list()
    used_mapping_targets = list()

    sensor_list = sorted(configuration.flatten_sensor_definitions(sensors))

    mapper_list.extend(_create_sensor_mappers(sensor_list, config, used_mapping_targets))
    mapper_list.extend(_create_compound_mappers(sensor_list, config, used_mapping_targets))
    mapper_list.extend(_create_internal_mappers(config, used_mapping_targets))

    logger.debug("Created %d mappers from %d sensors" % (len(mapper_list), len(sensors)))
    return mapper_list


def _create_sensor_mappers(sensors: List[configuration.FlatSensorDefinition],
                           config: configuration.Configuration,
                           used_mapping_targets: list) -> List[mappers.AbstractMapping]:
    mapper_list = list()
    for sensor in sensors:
        mapper = _create_sensor_mapper(sensor, config, used_mapping_targets)
        mapper_list.append(mapper)
        used_mapping_targets.extend(mapper.targets.values())

    return mapper_list


def _create_sensor_mapper(sensor: configuration.FlatSensorDefinition,
                          config: configuration.Configuration,
                          used_mapping_targets: list) -> mappers.AbstractMapping:
    log_success = config.log_success
    log_error = config.log_error
    tx_id, sensor_key = sensor

    logger.debug("Creating mapping for sensor %s (tx id: %s)" % (sensor_key, str(tx_id)))

    if sensor_key == config_static.SensorType.TEMPERATURE_HUMIDITY:
        return mappers.THMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_key == config_static.SensorType.RAIN:
        return mappers.RainMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_key == config_static.SensorType.WIND:
        return mappers.WindMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_key == config_static.SensorType.UV:
        return mappers.UvMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_key == config_static.SensorType.SOLAR:
        return mappers.SolarMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_key == config_static.SensorType.SOIL_TEMPERATURE_1:
        return mappers.SoilTempMapping([str(tx_id), str(1)], used_mapping_targets, log_success, log_error)
    elif sensor_key == config_static.SensorType.SOIL_TEMPERATURE_2:
        return mappers.SoilTempMapping([str(tx_id), str(2)], used_mapping_targets, log_success, log_error)
    elif sensor_key == config_static.SensorType.SOIL_TEMPERATURE_3:
        return mappers.SoilTempMapping([str(tx_id), str(3)], used_mapping_targets, log_success, log_error)
    elif sensor_key == config_static.SensorType.SOIL_TEMPERATURE_4:
        return mappers.SoilTempMapping([str(tx_id), str(4)], used_mapping_targets, log_success, log_error)

    elif sensor_key == config_static.SensorType.SOIL_MOISTURE_1:
        return mappers.SoilMoistureMapping([str(tx_id), str(1)], used_mapping_targets, log_success, log_error)
    elif sensor_key == config_static.SensorType.SOIL_MOISTURE_2:
        return mappers.SoilMoistureMapping([str(tx_id), str(2)], used_mapping_targets, log_success, log_error)
    elif sensor_key == config_static.SensorType.SOIL_MOISTURE_3:
        return mappers.SoilMoistureMapping([str(tx_id), str(3)], used_mapping_targets, log_success, log_error)
    elif sensor_key == config_static.SensorType.SOIL_MOISTURE_4:
        return mappers.SoilMoistureMapping([str(tx_id), str(4)], used_mapping_targets, log_success, log_error)

    elif sensor_key == config_static.SensorType.LEAF_WETNESS_1:
        return mappers.LeafWetnessMapping([str(tx_id), str(1)], used_mapping_targets, log_success, log_error)
    elif sensor_key == config_static.SensorType.LEAF_WETNESS_2:
        return mappers.LeafWetnessMapping([str(tx_id), str(2)], used_mapping_targets, log_success, log_error)

    else:
        raise ValueError("Unknown sensor key: %s" % sensor_key)


def _create_compound_mappers(sensors: List[configuration.FlatSensorDefinition],
                             config: configuration.Configuration,
                             used_mapping_targets: list) -> List[mappers.AbstractMapping]:
    log_success = config.log_success
    log_error = config.log_error

    mapper_list = list()

    for tx_id in _get_tx_ids_for_thsw(sensors):
        map_apparent_temperature = 'appTemp' not in used_mapping_targets
        mapping_opts = [str(tx_id), 'appTemp'] if map_apparent_temperature else [str(tx_id)]
        logger.debug("Creating THSW mapper for tx id %d (apparent temperature: %s)" % (tx_id,
                                                                                       repr(map_apparent_temperature)))

        mapping = mappers.ThswMapping(mapping_opts, used_mapping_targets, log_success, log_error)
        mapper_list.append(mapping)
        used_mapping_targets.extend(mapping.targets.values())

    for tx_id in _get_tx_ids_for_thw(sensors):
        map_apparent_temperature = 'appTemp' not in used_mapping_targets
        mapping_opts = [str(tx_id), 'appTemp'] if map_apparent_temperature else [str(tx_id)]
        logger.debug("Creating THW mappers for tx id %d (apparent temperature: %s)" % (tx_id,
                                                                                       repr(map_apparent_temperature)))

        thw_mapping = mappers.ThwMapping(mapping_opts, used_mapping_targets, log_success, log_error)
        mapper_list.append(thw_mapping)
        used_mapping_targets.extend(thw_mapping.targets.values())

        wind_chill_mapping = mappers.WindChillMapping([tx_id], used_mapping_targets, log_success, log_error)
        mapper_list.append(wind_chill_mapping)
        used_mapping_targets.extend(wind_chill_mapping.targets.values())

    return mapper_list


def _get_tx_ids_for_thsw(sensors: List[configuration.FlatSensorDefinition], ) -> Set[int]:
    tx_ids = {
        tx_id
        for tx_id
        in _get_tx_ids(sensors)
        if _has_sensors(sensors, tx_id, {config_static.SensorType.TEMPERATURE_HUMIDITY.value,
                                         config_static.SensorType.WIND.value,
                                         config_static.SensorType.SOLAR.value})
    }
    logger.debug("%d transmitters with THSW metric: %s" % (len(tx_ids), str(tx_ids)))
    return tx_ids


def _get_tx_ids_for_thw(sensors: Iterable[configuration.FlatSensorDefinition], ) -> Set[int]:
    tx_ids = {
        tx_id
        for tx_id
        in _get_tx_ids(sensors)
        if _has_sensors(sensors, tx_id, {config_static.SensorType.TEMPERATURE_HUMIDITY.value,
                                         config_static.SensorType.WIND.value})
    }
    logger.debug("%d transmitters with THW metric: %s" % (len(tx_ids), str(tx_ids)))
    return tx_ids


def _get_tx_ids(sensors: Iterable[configuration.FlatSensorDefinition], ) -> Set[int]:
    tx_ids = {sensor[0] for sensor in sensors}
    return tx_ids


def _has_sensors(sensors: Iterable[configuration.FlatSensorDefinition],
                 expected_tx_id: int,
                 expected_sensor_types: Set[str]) -> bool:
    for tx_id, sensor_key in sensors:
        if tx_id != expected_tx_id:
            continue

        if sensor_key in expected_sensor_types:
            expected_sensor_types.remove(sensor_key)

    return len(expected_sensor_types) == 0


def _create_internal_mappers(config: configuration.Configuration,
                             used_mapping_targets: list) -> List[mappers.AbstractMapping]:
    logger.debug("Creating implicit mappers")

    th_indoor_mapping = mappers.THIndoorMapping([], used_mapping_targets, config.log_success, config.log_error)
    used_mapping_targets.extend(th_indoor_mapping.targets.values())

    baro_mapping = mappers.BaroMapping([], used_mapping_targets, config.log_success, config.log_error)
    used_mapping_targets.extend(baro_mapping.targets.values())

    return [th_indoor_mapping, baro_mapping]
