from typing import Optional, Set, List, Dict, Tuple, Iterable

from user.weatherlink_live import cli
from user.weatherlink_live.configuration import SensorDefinition
from user.weatherlink_live.mappers import AbstractMapping
from user.weatherlink_live.static import labels


def print_mappings(mappers):
    mapping_tree = _create_mapping_tree(mappers)
    _print_mapping_tree(mapping_tree)


def _create_mapping_tree(mappers: List[AbstractMapping]) -> Dict[str, Dict[str, Dict[str, str | List[str]]]]:
    mapping_tree = dict()

    for mapper in mappers:
        mapper_source = mapper.map_source_transmitter
        mapper_type = type(mapper).__name__
        mapping_table = mapper.map_table

        if mapper_source not in mapping_tree:
            mapping_tree[mapper_source] = dict()

        if mapper_type not in mapping_tree[mapper_source]:
            mapping_tree[mapper_source][mapper_type] = dict()

        mapping_tree[mapper_source][mapper_type] = {**mapping_tree[mapper_source][mapper_type], **mapping_table}

    return mapping_tree


def _print_mapping_tree(mapping_tree: Dict[str, Dict[str, Dict[str, str | List[str]]]]) -> None:
    for transmitter, tx_mappings in mapping_tree.items():
        print(f"{cli.Colors.BOLD}{cli.Colors.HEADER}== %s =={cli.Colors.END}\n" % transmitter)

        for mapping_type, map_table in tx_mappings.items():
            print(f"  {cli.Colors.BOLD}{cli.Colors.HEADER}%s{cli.Colors.END}:" % mapping_type)

            for map_source, map_targets in map_table.items():
                map_target = ", ".join(map_targets) if type(map_targets) is list else str(map_targets)
                print(f"    {cli.Colors.BOLD}%s{cli.Colors.END}: %s" % (map_source, map_target))
            print("")
        print("")


def build_sensor_label(sensor_type: str, sensor_number: Optional[int]) -> str:
    if sensor_number is None:
        return labels.SENSOR_LABELS[sensor_type]
    else:
        return "%s - No. %d" % (labels.SENSOR_LABELS[sensor_type], sensor_number)


def build_tx_sensor_label(tx_id: int, sensor_type: str, sensor_number: Optional[int]) -> str:
    return "TX. %d - %s" % (tx_id, build_sensor_label(sensor_type, sensor_number))


def print_sensors(sensor_config: Set[SensorDefinition]):
    grouped_sensor_config = _group_sensor_config(sorted(sensor_config))

    if len(grouped_sensor_config) < 1:
        print("No sensors are configured")
        return

    print("")
    for tx_id, sensors in grouped_sensor_config.items():
        print(f"{cli.Colors.BOLD}{cli.Colors.HEADER}== Transmitter %d =={cli.Colors.END}" % tx_id)
        for sensor_type, sensor_number in sorted(sensors):
            sensor_label = build_sensor_label(sensor_type, sensor_number)
            print(" - %s" % sensor_label)
        print("")


def _group_sensor_config(sensor_config: Iterable[SensorDefinition]) -> Dict[int, List[Tuple[str, Optional[int]]]]:
    group_set: Dict[int, List[Tuple[str, Optional[int]]]] = dict()

    for tx_id, sensor_type, sensor_number in sensor_config:
        if tx_id not in group_set:
            group_set[tx_id] = list()
        group_set[tx_id].append((sensor_type, sensor_number))

    return group_set
