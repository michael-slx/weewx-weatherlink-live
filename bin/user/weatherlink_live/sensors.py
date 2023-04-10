import logging
from typing import List, Set

from user.weatherlink_live import configuration, mappers
from user.weatherlink_live.static import config as config_static

logger = logging.getLogger(__name__)


def create_mappers_from_sensors(sensors: configuration.SensorDefinitionSet,
                                config: configuration.Configuration) -> List[mappers.AbstractMapping]:
    mapper_list = list()
    used_mapping_targets = list()

    mapper_list.extend(_create_sensor_mappers(sensors, config, used_mapping_targets))
    mapper_list.extend(_create_compound_mappers(sensors, config, used_mapping_targets))
    mapper_list.extend(_create_internal_mappers(config, used_mapping_targets))

    logger.debug("Created %d mappers from %d sensors" % (len(mapper_list), len(sensors)))
    return mapper_list


def _create_sensor_mappers(sensors: configuration.SensorDefinitionSet,
                           config: configuration.Configuration,
                           used_mapping_targets: list) -> List[mappers.AbstractMapping]:
    mapper_list = list()
    for sensor in sensors:
        mapper = _create_sensor_mapper(sensor, config, used_mapping_targets)
        mapper_list.append(mapper)
        used_mapping_targets.extend(mapper.targets.values())

    return mapper_list


def _create_sensor_mapper(sensors: configuration.SensorDefinitionSet,
                          config: configuration.Configuration,
                          used_mapping_targets: list) -> mappers.AbstractMapping:
    log_success = config.log_success
    log_error = config.log_error
    tx_id, sensor_type, sensor_num = sensors

    logger.debug("Creating mapping for sensor %s (tx id: %s; num.: %s)" % (sensor_type,
                                                                           str(tx_id),
                                                                           str(sensor_num) if sensor_num is not None else "None"))

    if sensor_type == config_static.SENSOR_TYPE_TEMPERATURE_HUMIDITY:
        return mappers.THMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_type == config_static.SENSOR_TYPE_RAIN:
        return mappers.RainMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_type == config_static.SENSOR_TYPE_WIND:
        return mappers.WindMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_type == config_static.SENSOR_TYPE_UV:
        return mappers.UvMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_type == config_static.SENSOR_TYPE_SOLAR:
        return mappers.SolarMapping([str(tx_id)], used_mapping_targets, log_success, log_error)

    elif sensor_type == config_static.SENSOR_TYPE_SOIL_TEMPERATURE:
        if sensor_num is None:
            raise ValueError("Sensor number is required for sensor type %s" % sensor_type)
        if sensor_num not in range(1, 4 + 1):
            raise ValueError("Sensor number for sensor type %s has to be in range 1 - 4 (got: %d)" % (sensor_type,
                                                                                                      sensor_num))

        return mappers.SoilTempMapping([str(tx_id), str(sensor_num)], used_mapping_targets, log_success, log_error)

    elif sensor_type == config_static.SENSOR_TYPE_SOIL_MOISTURE:
        if sensor_num is None:
            raise ValueError("Sensor number is required for sensor type %s" % sensor_type)
        if sensor_num not in range(1, 4 + 1):
            raise ValueError("Sensor number for sensor type %s has to be in range 1 - 4 (got: %d)" % (sensor_type,
                                                                                                      sensor_num))

        return mappers.SoilMoistureMapping([str(tx_id), str(sensor_num)], used_mapping_targets, log_success, log_error)

    elif sensor_type == config_static.SENSOR_TYPE_LEAF_WETNESS:
        if sensor_num is None:
            raise ValueError("Sensor number is required for sensor type %s" % sensor_type)
        if sensor_num not in range(1, 2 + 1):
            raise ValueError("Sensor number for sensor type %s has to be in range 1 - 2 (got: %d)" % (sensor_type,
                                                                                                      sensor_num))

        return mappers.LeafWetnessMapping([str(tx_id), str(sensor_num)], used_mapping_targets, log_success, log_error)

    else:
        raise ValueError("Unknown sensor type: %s" % sensor_type)


def _create_compound_mappers(sensors: configuration.SensorDefinitionSet,
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


def _get_tx_ids_for_thsw(sensors: configuration.SensorDefinitionSet) -> Set[int]:
    tx_ids = {
        tx_id
        for tx_id
        in _get_tx_ids(sensors)
        if _has_sensors(sensors, tx_id, {config_static.SENSOR_TYPE_TEMPERATURE_HUMIDITY,
                                         config_static.SENSOR_TYPE_WIND,
                                         config_static.SENSOR_TYPE_SOLAR})
    }
    logger.debug("%d transmitters with THSW metric: %s" % (len(tx_ids), str(tx_ids)))
    return tx_ids


def _get_tx_ids_for_thw(sensors: configuration.SensorDefinitionSet) -> Set[int]:
    tx_ids = {
        tx_id
        for tx_id
        in _get_tx_ids(sensors)
        if _has_sensors(sensors, tx_id, {config_static.SENSOR_TYPE_TEMPERATURE_HUMIDITY,
                                         config_static.SENSOR_TYPE_WIND})
    }
    logger.debug("%d transmitters with THW metric: %s" % (len(tx_ids), str(tx_ids)))
    return tx_ids


def _get_tx_ids(sensors: configuration.SensorDefinitionSet) -> Set[int]:
    tx_ids = {sensor[0] for sensor in sensors}
    return tx_ids


def _has_sensors(sensors: configuration.SensorDefinitionSet,
                 expected_tx_id: int,
                 expected_sensor_types: Set[str]) -> bool:
    for tx_id, sensor_type, _ in sensors:
        if tx_id != expected_tx_id:
            continue

        if sensor_type in expected_sensor_types:
            expected_sensor_types.remove(sensor_type)

    return len(expected_sensor_types) == 0


def _create_internal_mappers(config: configuration.Configuration,
                             used_mapping_targets: list) -> List[mappers.AbstractMapping]:
    logger.debug("Creating implicit mappers")

    th_indoor_mapping = mappers.THIndoorMapping([], used_mapping_targets, config.log_success, config.log_error)
    used_mapping_targets.extend(th_indoor_mapping.targets.values())

    baro_mapping = mappers.BaroMapping([], used_mapping_targets, config.log_success, config.log_error)
    used_mapping_targets.extend(baro_mapping.targets.values())

    return [th_indoor_mapping, baro_mapping]
