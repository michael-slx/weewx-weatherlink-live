from optparse import OptionParser
from typing import Dict, List

from user.weatherlink_live import configuration
from user.weatherlink_live.mappers import AbstractMapping
from user.weatherlink_live.static import version
from weewx.drivers import AbstractConfigurator


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
    print("")
    print("=== Configured Mappings ===")
    print("")

    for transmitter, tx_mappings in mapping_tree.items():
        print("== %s ==" % transmitter)
        print("")

        for mapping_type, map_table in tx_mappings.items():
            print("  %s:" % mapping_type)

            for map_source, map_targets in map_table.items():
                map_target = ", ".join(map_targets) if type(map_targets) is list else str(map_targets)
                print("    %s: %s" % (map_source, map_target))

            print("")

        print("")


def _print_mapping(conf_dict: Dict) -> None:
    config = configuration.create_configuration(conf_dict, version.DRIVER_NAME)
    mappers = config.create_mappers()

    mapping_tree = _create_mapping_tree(mappers)
    _print_mapping_tree(mapping_tree)


class WeatherlinkLiveConfigurator(AbstractConfigurator):
    @property
    def description(self):
        return "Configuration utility for WeatherLink LIVE driver"

    @property
    def usage(self):
        return """%prog --help
       %prog [config_file] --print-mapping
"""

    @property
    def epilog(self):
        return ""

    def add_options(self, parser: OptionParser):
        super(WeatherlinkLiveConfigurator, self).add_options(parser)

        parser.add_option("--print-mapping",
                          action="store_true", dest="print_mapping",
                          help="Display configured mapping")

    def do_options(self, options, parser, config_dict, prompt):
        if options.print_mapping:
            _print_mapping(config_dict)
            return
