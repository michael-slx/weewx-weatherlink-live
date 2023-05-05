from typing import Dict

from user.weatherlink_live.static import config, labels

SHORT_SENSORS_TO_KEYS: Dict[str, config.SensorType] = {
    "th": config.SensorType.TEMPERATURE_HUMIDITY,
    "w": config.SensorType.WIND,
    "r": config.SensorType.RAIN,
    "s": config.SensorType.SOLAR,
    "u": config.SensorType.UV,
    "st1": config.SensorType.SOIL_TEMPERATURE_1,
    "st2": config.SensorType.SOIL_TEMPERATURE_2,
    "st3": config.SensorType.SOIL_TEMPERATURE_3,
    "st4": config.SensorType.SOIL_TEMPERATURE_4,
    "sm1": config.SensorType.SOIL_MOISTURE_1,
    "sm2": config.SensorType.SOIL_MOISTURE_2,
    "sm3": config.SensorType.SOIL_MOISTURE_3,
    "sm4": config.SensorType.SOIL_MOISTURE_4,
    "lw1": config.SensorType.LEAF_WETNESS_1,
    "lw2": config.SensorType.LEAF_WETNESS_2,
}

SENSOR_KEYS_TO_SHORT: Dict[config.SensorType, str] = {sensor_key: short
                                                      for short, sensor_key
                                                      in SHORT_SENSORS_TO_KEYS.items()}

SHORT_SENSORS_DESCRIPTION: Dict[str, str] = {sensor_short: labels.SENSOR_LABELS[sensor_key]
                                             for sensor_short, sensor_key
                                             in SHORT_SENSORS_TO_KEYS.items()}
