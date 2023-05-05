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

from typing import Any, Dict, Optional

from configobj import ConfigObj

import weecfg
import weewx.drivers
from user.weatherlink_live import sensor_prompt, cli
from user.weatherlink_live.configuration import parse_sensor_definition_map, sensor_definition_map_to_config, \
    sensor_definition_map_to_config_comments
from user.weatherlink_live.static import config


def _prompt_host(old_host: Optional[str]) -> str:
    print("Specify the IP address (e.g. 192.168.1.123) or hostname (e.g. weatherlinklive")
    print("or weatherlinklive.localdomain) of the WeatherLink LIVE.)")
    return weecfg.prompt_with_options(f"{cli.Colors.BOLD}Enter IP or Hostname{cli.Colors.END}", old_host)


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

        print("")
        print("")
        print("")

        old_host = settings.get(config.KEY_DRIVER_HOST, None)
        old_host = old_host if old_host and len(old_host) > 0 else None
        host = _prompt_host(old_host)
        settings[config.KEY_DRIVER_HOST] = host

        print("")
        print("")
        print("")

        if config.KEY_DRIVER_MAPPING in settings:
            del settings[config.KEY_DRIVER_MAPPING]

        old_sensor_section = settings.get(config.KEY_SECTION_SENSORS, dict())
        old_sensor_settings = parse_sensor_definition_map(old_sensor_section)
        new_sensor_settings = sensor_prompt.prompt_sensors(old_sensor_settings)
        settings[config.KEY_SECTION_SENSORS] = sensor_definition_map_to_config(new_sensor_settings)
        settings[config.KEY_SECTION_SENSORS].comments = sensor_definition_map_to_config_comments(new_sensor_settings)

        return settings

    def modify_config(self, config_dict):
        print("\n")
        print("""Configuring accumulators for custom types.""")

        config_dict.setdefault('Accumulator', {})

        config_dict['Accumulator'].setdefault('rainCount', {})
        config_dict['Accumulator']['rainCount']['extractor'] = 'sum'

        config_dict['Accumulator'].setdefault('rainSize', {})
        config_dict['Accumulator']['rainSize']['extractor'] = 'last'
