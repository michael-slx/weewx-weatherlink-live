from typing import Any, Dict, List

import weewx.drivers
from user.weatherlink_live import discovery, davis_http


class WeatherlinkLiveConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
#   This section configures the WeatherLink Live driver

[WeatherLinkLive]
    # Driver module
    driver = user.weatherlink_live

    # Host name or IP address of WeatherLink Live
    host = weatherlink

    # Mapping of transmitter ids to WeeWX records
    # Default for Vantage Pro2
    mapping = th:1, th_indoor, baro, rain:1, wind:1, thw:1:appTemp, windchill:1, battery:1:outTemp:rain:wind
"""

    def prompt_for_settings(self) -> Dict[str, Any]:
        settings = dict()

        host = self._prompt_host()
        settings['host'] = host

        self._prompt_continue_discovery()
        mappings = self._discover_sensors(host)
        settings['mapping'] = mappings

        return settings

    def _prompt_host(self) -> str:
        print("")
        print("Specify the IP address (e.g. 192.168.1.123) or hostname (e.g. weatherlinklive")
        print("or weatherlinklive.localdomain) of the WeatherLink LIVE.)")
        print("The device must be reachable via HTTP (TCP port 80) and must be on the same")
        print("subnet/VLAN. If this is not the case, 2.5-second live updates will not work")
        print("(sent as broadcast packets on UDP port 22222).")
        host = self._prompt("host")
        return host

    def _prompt_continue_discovery(self) -> None:
        print("")
        print("This driver can automatically configure WeeWX to import all sensors connected")
        print("to your WeatherLink LIVE.")
        print("Note that only sensors that are currently sending data can be discovered")
        print("automatically. Please confirm that all sensors are working using the")
        print("WeatherLink.com dashboard or the WeatherLink app before continuing.")
        input("Press ENTER to continue")

    def _discover_sensors(self, host: str) -> List[str]:
        print("")
        print("Discovering sensors ...")
        packet = davis_http.request_current(host)
        mapping_definitions = discovery.discover_sensors(packet)

        mappings = [":".join(mapping_definition) for mapping_definition in mapping_definitions]
        print("Discovered sensors: %s" % ", ".join(mappings))

        return mappings

    def modify_config(self, config_dict):
        print("""
Configuring accumulators for custom types.""")
        config_dict.setdefault('Accumulator', {})

        config_dict['Accumulator'].setdefault('rainCount', {})
        config_dict['Accumulator']['rainCount']['extractor'] = 'sum'

        config_dict['Accumulator'].setdefault('rainSize', {})
        config_dict['Accumulator']['rainSize']['extractor'] = 'last'
