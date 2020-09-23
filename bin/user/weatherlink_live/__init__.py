"""
WeeWX driver for WeatherLink Live and AirLink
"""
import logging

from user.weatherlink_live import davis_http, data_host
from user.weatherlink_live.configuration import create_configuration
from user.weatherlink_live.service import WllWindService
from weewx.drivers import AbstractDevice

DRIVER_NAME = "WeatherLinkLive"
DRIVER_VERSION = "1.0.0-rc1"

log = logging.getLogger(__name__)


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
