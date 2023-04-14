from typing import Optional

from user.weatherlink_live.static import labels


def build_sensor_label(sensor_type: str, sensor_number: Optional[int]) -> str:
    if sensor_number is None:
        return labels.SENSOR_LABELS[sensor_type]
    else:
        return "%s - No. %d" % (labels.SENSOR_LABELS[sensor_type], sensor_number)


def build_tx_sensor_label(tx_id: int, sensor_type: str, sensor_number: Optional[int]) -> str:
    return "TX. %d - %s" % (tx_id, build_sensor_label(sensor_type, sensor_number))
