from optparse import OptionParser
from typing import Dict

from user.weatherlink_live import configuration
from user.weatherlink_live.static import version
from weewx.drivers import AbstractConfigurator


def _print_mapping(conf_dict: Dict) -> None:
    config = configuration.create_configuration(conf_dict, version.DRIVER_NAME)
    mappers = config.create_mappers()

    mappings = {}

    for mapper in mappers:
        mappings = {**mappings, **mapper.map_table}

    for (mapping_source, mapping_targets) in mappings.items():
        mapping_target = ", ".join(mapping_targets) if type(mapping_targets) is list else mapping_targets
        print("%s: %s" % (mapping_source, mapping_target))


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
