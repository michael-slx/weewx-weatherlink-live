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

from optparse import OptionParser
from typing import List

from user.weatherlink_live import configuration
from user.weatherlink_live.config_display import print_mappings, print_sensors
from user.weatherlink_live.configuration import create_mappers
from user.weatherlink_live.mappers import AbstractMapping
from user.weatherlink_live.sensors import create_mappers_from_sensors
from user.weatherlink_live.static import version
from weewx.drivers import AbstractConfigurator


def _print_configuration(config: configuration.Configuration) -> None:
    config_print_str = """

=== Configuration ===
Hostname/IP address: %s
Polling interval: %d s
Max. no data iterations: %d
Socket timeout: %d s
Log successful operations: %s
Log erroneous operations: %s
""" % (config.host,
       config.polling_interval,
       config.max_no_data_iterations,
       config.socket_timeout,
       repr(config.log_success),
       repr(config.log_error))
    print(config_print_str)


def _print_sensors(config: configuration.Configuration) -> None:
    sensors = config.sensor_definition_set

    print("\n\n=== Configured Sensors ===")
    if len(sensors) > 0:
        print_sensors({*sensors})

    else:
        print("No sensors are configured")


def _print_mapping(config: configuration.Configuration) -> None:
    mappers = _create_mappers(config)

    print("\n\n=== Configured Mappings ===")
    if len(mappers) > 0:
        print("")
        print_mappings(mappers)

    else:
        print("No mappings are configured")


def _create_mappers(config: configuration.Configuration) -> List[AbstractMapping]:
    if config.has_mappings:
        return create_mappers(config.mappings,
                              config.log_success,
                              config.log_error)

    else:
        return create_mappers_from_sensors(config.sensor_definition_set, config)


class WeatherlinkLiveConfigurator(AbstractConfigurator):
    @property
    def description(self):
        return "Configuration utility for WeatherLink LIVE driver"

    @property
    def usage(self):
        return """%prog --help
       %prog [config_file] -c|--print-configuration
       %prog [config_file] -s|--print-sensors
       %prog [config_file] -m|--print-mapping
"""

    @property
    def epilog(self):
        return ""

    def add_options(self, parser: OptionParser):
        super(WeatherlinkLiveConfigurator, self).add_options(parser)

        parser.add_option("-c", "--print-configuration",
                          action="store_true", dest="print_config",
                          help="Display all configuration options")
        parser.add_option("-s", "--print-sensors",
                          action="store_true", dest="print_sensors",
                          help="Display configured sensors")
        parser.add_option("-m", "--print-mapping",
                          action="store_true", dest="print_mapping",
                          help="Display configured mapping")

    def do_options(self, options, parser, config_dict, prompt):
        config = configuration.create_configuration(config_dict, version.DRIVER_NAME)

        if options.print_config:
            _print_configuration(config)
        if options.print_sensors:
            _print_sensors(config)
        if options.print_mapping:
            _print_mapping(config)
