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

from typing import List, Dict

from user.weatherlink_live import cli
from user.weatherlink_live.configuration import SensorDefinitionMap
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


def print_sensors(sensor_definition_map: SensorDefinitionMap) -> None:
    if not sensor_definition_map:
        print("No sensors are configured")
        return

    print("")
    for tx_id, sensors in sensor_definition_map.items():
        print(f"{cli.Colors.BOLD}{cli.Colors.HEADER}== Transmitter %d =={cli.Colors.END}" % tx_id)
        for sensor_key in sorted(sensors):
            sensor_label = labels.SENSOR_LABELS[sensor_key]
            print(" • %s" % sensor_label)
        print("")
