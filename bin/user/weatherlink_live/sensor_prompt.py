from user.weatherlink_live import configuration, cli
from user.weatherlink_live.static import interactive


def prompt_sensors(old_sensor_definition_map: configuration.SensorDefinitionMap) -> configuration.SensorDefinitionMap:
    new_sensor_definition_map = dict()

    try:
        for tx_id in range(1, 8 + 1):
            old_tx_sensors = old_sensor_definition_map.get(tx_id, set())
            new_tx_sensors = _prompt_sensors_of_tx(tx_id, old_tx_sensors)

            if new_tx_sensors:
                new_sensor_definition_map[tx_id] = new_tx_sensors

    except KeyboardInterrupt:
        pass
    except EOFError:
        pass

    return new_sensor_definition_map


def _prompt_sensors_of_tx(tx_id: int,
                          old_tx_sensors: configuration.SensorDefinitionSet) -> configuration.SensorDefinitionSet:
    short_sensor_list = sorted({interactive.SENSOR_KEYS_TO_SHORT[sensor_key]
                                for sensor_key
                                in old_tx_sensors})
    prompt = "Enter sensors of transmitter %d" % tx_id
    new_short_sensor_list = cli.prompt_list(prompt, interactive.SHORT_SENSORS_DESCRIPTION, short_sensor_list)
    sensor_set = {interactive.SHORT_SENSORS_TO_KEYS[short_sensor] for short_sensor in new_short_sensor_list}
    return sensor_set
