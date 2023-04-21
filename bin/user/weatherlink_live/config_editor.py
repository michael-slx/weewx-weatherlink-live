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

from typing import Any, Dict, Optional, Set

from configobj import ConfigObj

import weecfg
import weewx.drivers
from user.weatherlink_live import cli, configuration
from user.weatherlink_live.config_display import build_tx_sensor_label, print_sensors
from user.weatherlink_live.configuration import TxSensorDefinition
from user.weatherlink_live.static import config

_URL_HELP_INSTALLATION = "https://github.com/michael-slx/weewx-weatherlink-live/blob/develop/docs/installation.md"


def _prompt_host(old_host: Optional[str]) -> str:
    print("\n")
    print("Specify the IP address (e.g. 192.168.1.123) or hostname (e.g. weatherlinklive")
    print("or weatherlinklive.localdomain) of the WeatherLink LIVE.)")
    print("The device must be reachable via HTTP (TCP port 80) and must be on the same")
    print("subnet/VLAN. If this is not the case, 2.5-second live updates will not work")
    print("(sent as broadcast packets on UDP port 22222).")
    return weecfg.prompt_with_options("IP/Hostname", old_host)


def _menu_sensor_action() -> str:
    return cli.menu("Action", {
        'w': "Quit & Save changes",
        'q': "Quit & Discard changes",
        'p': "Print sensors",
        'n': "Add a new sensor",
        'd': "Delete a sensor",
    })



def _add_sensor(sensor_config: Set[TxSensorDefinition], last_tx_id: Optional[int] = None) -> (int, str, Optional[int]):
    tx_id = cli.prompt_int_range("Enter the transmitter id of the sensor", 1, 8, last_tx_id)
    sensor_type_short = cli.menu("Enter the type of sensor", {
        'th': "Temperature/Humidity",
        'r': "Rain",
        'w': "Wind",
        's': "Solar irradiation",
        'u': "UV index",
        'st': "Soil temperature",
        'sm': "Soil moisture",
        'lw': "Leaf wetness",
    })
    sensor_type_map = {
        'th': config.SENSOR_TYPE_TEMPERATURE_HUMIDITY,
        'r': config.SENSOR_TYPE_RAIN,
        'w': config.SENSOR_TYPE_WIND,
        's': config.SENSOR_TYPE_SOLAR,
        'u': config.SENSOR_TYPE_UV,
        'st': config.SENSOR_TYPE_SOIL_TEMPERATURE,
        'sm': config.SENSOR_TYPE_SOIL_MOISTURE,
        'lw': config.SENSOR_TYPE_LEAF_WETNESS,
    }

    if sensor_type_short in ['st', 'sm']:
        sensor_number = cli.prompt_int_range("Enter the port number of the sensor", 1, 4)

    elif sensor_type_short == 'lw':
        sensor_number = cli.prompt_int_range("Enter the port number of the sensor", 1, 2)

    else:
        sensor_number = None

    sensor_type = sensor_type_map[sensor_type_short]

    sensor_config.add((tx_id, sensor_type, sensor_number))
    print("Created sensor: %s" % build_tx_sensor_label(tx_id, sensor_type, sensor_number))

    return tx_id, sensor_type, sensor_number


def _delete_sensor(sensor_config: Set[TxSensorDefinition]):
    sensor_config_list = sorted(sensor_config)
    sensor_config_menu_list = [
        build_tx_sensor_label(tx_id, sensor_type, sensor_number)
        for tx_id, sensor_type, sensor_number
        in sensor_config_list
    ]

    print("\nSelect sensor to delete:")
    for i in range(len(sensor_config_menu_list)):
        print(" %2d: %s" % (i, sensor_config_menu_list[i]))

    delete_idx = cli.prompt_int_range("Delete sensor", 0, len(sensor_config_menu_list) - 1)
    delete_sensor = sensor_config_list[delete_idx]
    sensor_config.remove(delete_sensor)

    print("Deleted sensor: %s" % build_tx_sensor_label(*delete_sensor))


def _prompt_sensors_interactive(old_sensor_config: Set[TxSensorDefinition]) -> Set[TxSensorDefinition]:
    sensor_config: Set[TxSensorDefinition] = {*old_sensor_config}
    last_tx_id: Optional[int] = None

    while True:
        print("")
        action = _menu_sensor_action()

        if action == 'w'.casefold():
            break

        elif action == 'q'.casefold():
            return old_sensor_config

        elif action == 'p'.casefold():
            print_sensors(sensor_config)

        elif action == 'n'.casefold():
            try:
                last_tx_id, _, _ = _add_sensor(sensor_config, last_tx_id)
            except cli.AbortCliMenu:
                continue

        elif action == 'd'.casefold():
            try:
                _delete_sensor(sensor_config)
            except cli.AbortCliMenu:
                continue

    return sensor_config


def _print_mapping_table_info():
    print("\n")
    print("""You can display all mappings by running the following command:
$ wee_device --print-mapping""")


def _print_schema_info():
    print("\n")
    print("""In order to utilize the full potential of your WeatherLink LIVE, you should use
the database schema included with this driver.

See the installation manual for detailed instructions:
%s""" % _URL_HELP_INSTALLATION)


class WeatherlinkLiveConfEditor(weewx.drivers.AbstractConfEditor):
    def __init__(self):
        self.existing_options = ConfigObj()

    @property
    def default_stanza(self):
        return """
#   This section configures the WeatherLink Live driver

[WeatherLinkLive]
    # Driver module
    driver = user.weatherlink_live

    # Host name or IP address of WeatherLink Live
    host = weatherlinklive

    # Whether to log successful operations. Overrides top-level setting.
    #log_success = False

    # Whether to log unsuccessful operations. Overrides top-level setting.
    #log_failure = True

    # Configuration of available sensors
    [[sensors]]
        # TX 1 has Temperature/Humidity, Rain, Wind, Solar and UV
        1 = th, rain, wind, solar, uv
"""

    def prompt_for_settings(self) -> Dict[str, Any]:
        settings = self.existing_options

        old_host = settings.get(config.KEY_DRIVER_HOST, None)
        old_host = old_host if old_host and len(old_host) > 0 else None
        host = _prompt_host(old_host)
        settings[config.KEY_DRIVER_HOST] = host

        if config.KEY_DRIVER_MAPPING in settings:
            del settings[config.KEY_DRIVER_MAPPING]

        old_sensors_section = settings.get(config.KEY_SECTION_SENSORS, dict())
        old_sensor_config = configuration.parse_sensor_definitions(old_sensors_section)
        sensor_config = _prompt_sensors_interactive({*old_sensor_config})
        new_sensors_section = configuration.build_sensor_definitions(sensor_config)

        settings[config.KEY_SECTION_SENSORS] = new_sensors_section
        settings.comments[config.KEY_SECTION_SENSORS] = ["", "Configuration of available sensors"]
        settings[config.KEY_SECTION_SENSORS].comments = configuration.build_sensor_definition_comments(sensor_config)

        print("")
        print("=== Configured sensors ===")
        print_sensors(sensor_config)

        print("")

        _print_mapping_table_info()
        _print_schema_info()

        return settings

    def modify_config(self, config_dict):
        print("\n")
        print("""Configuring accumulators for custom types.""")

        config_dict.setdefault('Accumulator', {})

        config_dict['Accumulator'].setdefault('rainCount', {})
        config_dict['Accumulator']['rainCount']['extractor'] = 'sum'

        config_dict['Accumulator'].setdefault('rainSize', {})
        config_dict['Accumulator']['rainSize']['extractor'] = 'last'
