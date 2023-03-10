import weewx.drivers


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

    def modify_config(self, config_dict):
        print("""
Configuring accumulators for custom types.""")
        config_dict.setdefault('Accumulator', {})

        config_dict['Accumulator'].setdefault('rainCount', {})
        config_dict['Accumulator']['rainCount']['extractor'] = 'sum'

        config_dict['Accumulator'].setdefault('rainSize', {})
        config_dict['Accumulator']['rainSize']['extractor'] = 'last'
