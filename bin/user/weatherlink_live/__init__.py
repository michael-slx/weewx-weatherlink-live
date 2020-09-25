# Copyright © 2020 Michael Schantl and contributors
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

"""
WeeWX driver for WeatherLink Live and AirLink
"""
import logging

import weewx.units
from schemas import wview_extended
from user.weatherlink_live import davis_http, data_host
from user.weatherlink_live.configuration import create_configuration
from user.weatherlink_live.service import WllWindService
from weewx.drivers import AbstractDevice

DRIVER_NAME = "WeatherLinkLive"
DRIVER_VERSION = "1.0.0"

log = logging.getLogger(__name__)

_temperature_fields = ["dewpoint2",
                       "dewpoint3",
                       "dewpoint4",
                       "dewpoint5",
                       "dewpoint6",
                       "dewpoint7",
                       "dewpoint8",
                       "heatindex2",
                       "heatindex3",
                       "heatindex4",
                       "heatindex5",
                       "heatindex6",
                       "heatindex7",
                       "heatindex8",
                       "wetbulb",
                       "wetbulb1",
                       "wetbulb2",
                       "wetbulb3",
                       "wetbulb4",
                       "wetbulb5",
                       "wetbulb6",
                       "wetbulb7",
                       "wetbulb8",
                       "thw",
                       "thsw",
                       "inHeatindex"]

schema = {
    'table': wview_extended.table + [(field, "REAL") for field in _temperature_fields],
    'day_summaries': wview_extended.day_summaries + [(field, "SCALAR") for field in _temperature_fields]
}
weewx.units.obs_group_dict.update(dict([(observation, "group_temperature") for observation in _temperature_fields]))


def loader(config_dict, engine):
    return WeatherlinkLiveDriver(config_dict, engine)


class WeatherlinkLiveDriver(AbstractDevice):
    """
    Main driver class
    """

    def __init__(self, conf_dict, engine):
        """Initialize driver"""

        self.run = True
        log.info("Initializing driver: %s v%s" % (DRIVER_NAME, DRIVER_VERSION))

        self.configuration = create_configuration(conf_dict, DRIVER_NAME)
        log.debug("Configuration: %s" % (repr(self.configuration)))

        self.mappers = self.configuration.create_mappers()
        self.wind_service = WllWindService(engine, conf_dict, self.mappers, self.configuration.log_success,
                                           self.configuration.log_error)

        self.is_running = False
        self.poll_host = None
        self.push_host = None

    @property
    def hardware_name(self):
        """Name of driver"""
        return DRIVER_NAME

    def genLoopPackets(self):
        """Open connection and generate loop packets"""

        if not self.is_running:
            self.start()

        while True:
            self.poll_host.raise_error()
            self.push_host.raise_error()

            while self.poll_host.packets:
                yield self.poll_host.packets.popleft()
            while self.push_host.packets:
                yield self.push_host.packets.popleft()

    def start(self):
        if self.is_running:
            return

        self.is_running = True
        self.poll_host = data_host.WllPollHost(self.configuration.host, self.configuration.polling_interval,
                                               self.mappers)
        self.push_host = data_host.WLLBroadcastHost(self.configuration.host, self.mappers)

    def closePort(self):
        """Close connection"""

        self.is_running = False
        if self.poll_host is not None:
            self.poll_host.close()
        if self.push_host is not None:
            self.push_host.close()
