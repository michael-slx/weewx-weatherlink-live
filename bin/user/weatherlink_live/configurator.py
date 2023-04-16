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

from user.weatherlink_live import configuration, network_test, cli
from user.weatherlink_live.config_display import print_mappings, print_sensors
from user.weatherlink_live.configuration import create_mappers
from user.weatherlink_live.mappers import AbstractMapping
from user.weatherlink_live.sensors import create_mappers_from_sensors
from user.weatherlink_live.static import version
from weewx.drivers import AbstractConfigurator


def _print_configuration(config: configuration.Configuration) -> None:
    config_print_str = f"""

{cli.Colors.STANDOUT}{cli.Colors.HEADER}=== Configuration ==={cli.Colors.END}

{cli.Colors.BOLD}Hostname/IP address:{cli.Colors.END} %s
{cli.Colors.BOLD}Polling interval:{cli.Colors.END} %d s
{cli.Colors.BOLD}Max. no data iterations:{cli.Colors.END} %d
{cli.Colors.BOLD}Socket timeout:{cli.Colors.END} %d s
{cli.Colors.BOLD}Log successful operations:{cli.Colors.END} %s
{cli.Colors.BOLD}Log erroneous operations:{cli.Colors.END} %s
""" % (config.host,
       config.polling_interval,
       config.max_no_data_iterations,
       config.socket_timeout,
       repr(config.log_success),
       repr(config.log_error))
    print(config_print_str)


def _print_sensors(config: configuration.Configuration) -> None:
    sensors = config.sensor_definition_set

    print(f"\n\n{cli.Colors.STANDOUT}{cli.Colors.HEADER}=== Configured Sensors ==={cli.Colors.END}")
    if len(sensors) > 0:
        print_sensors({*sensors})

    else:
        print(f"{cli.Colors.BOLD}No sensors are configured{cli.Colors.END}")


def _print_mapping(config: configuration.Configuration) -> None:
    mappers = _create_mappers(config)

    print(f"\n\n{cli.Colors.STANDOUT}{cli.Colors.HEADER}=== Configured Mappings ==={cli.Colors.END}")
    if len(mappers) > 0:
        print("")
        print_mappings(mappers)

    else:
        print(f"{cli.Colors.BOLD}No mappings are configured{cli.Colors.END}")


def _create_mappers(config: configuration.Configuration) -> List[AbstractMapping]:
    if config.has_mappings:
        return create_mappers(config.mappings,
                              config.log_success,
                              config.log_error)

    else:
        return create_mappers_from_sensors(config.sensor_definition_set, config)


def _test_network(config: configuration.Configuration) -> None:
    try:
        try:
            print("\n")
            network_test.test_http(config)
        except Exception as e:
            print(
                f"\n{cli.Colors.STANDOUT}{cli.Colors.FAIL}Error while requesting current conditions from WeatherLink Live \"%s\"{cli.Colors.END}" % config.host)
            print(f"{cli.Colors.FAIL}%s{cli.Colors.END}" % repr(e))
            return

        try:
            print("\n")
            network_test.test_udp(config)
        except Exception as e:
            print(
                f"\n{cli.Colors.STANDOUT}{cli.Colors.FAIL}Error while receiving live data from WeatherLink Live \"%s\"{cli.Colors.END}" % config.host)
            print(f"{cli.Colors.FAIL}%s{cli.Colors.END}" % repr(e))
            return

    except KeyboardInterrupt:
        pass


class WeatherlinkLiveConfigurator(AbstractConfigurator):
    @property
    def description(self):
        return "Configuration utility for WeatherLink LIVE driver"

    @property
    def usage(self):
        return """%prog --help
       %prog [config_file] [-t|--test]
       %prog [config_file] [-c|--print-configuration] [-s|--print-sensors] [-m|--print-mapping]
"""

    @property
    def epilog(self):
        return ""

    def add_options(self, parser: OptionParser):
        super(WeatherlinkLiveConfigurator, self).add_options(parser)

        parser.add_option("-t", "--test",
                          action="store_true", dest="test_network",
                          help="Test network connectivity")
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

        if options.test_network:
            _test_network(config)
            return

        if options.print_config:
            _print_configuration(config)
        if options.print_sensors:
            _print_sensors(config)
        if options.print_mapping:
            _print_mapping(config)
