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
import threading

import weewx.units
from schemas import wview_extended
from user.weatherlink_live import davis_http, data_host, scheduler
from user.weatherlink_live.configuration import create_configuration
from user.weatherlink_live.service import WllWindGustService
from weewx import WeeWxIOError
from weewx.drivers import AbstractDevice
from weewx.engine import InitializationError

DRIVER_NAME = "WeatherLinkLive"
DRIVER_VERSION = "1.0.5"

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
_rain_count_fields = ['rainCount']  # unit: count
_rain_count_rate_fields = ['rainCountRate']  # unit: count per hour
_rain_amount_fields = ['rainSize']  # unit: technically rain amount (inch/mm)

schema = {
    'table': wview_extended.table
             + [(field, "REAL") for field in _temperature_fields]
             + [(field, "REAL") for field in _rain_count_fields]
             + [(field, "REAL") for field in _rain_count_rate_fields]
             + [(field, "REAL") for field in _rain_amount_fields],
    'day_summaries': wview_extended.day_summaries
                     + [(field, "SCALAR") for field in _temperature_fields]
                     + [(field, "SCALAR") for field in _rain_count_fields]
                     + [(field, "SCALAR") for field in _rain_count_rate_fields]
                     + [(field, "SCALAR") for field in _rain_amount_fields]
}

# Define units of new observation
weewx.units.obs_group_dict.update(dict([(observation, "group_temperature") for observation in _temperature_fields]))
weewx.units.obs_group_dict.update(dict([(observation, "group_count") for observation in _rain_count_fields]))
weewx.units.obs_group_dict.update(dict([(observation, "group_rate") for observation in _rain_count_rate_fields]))
weewx.units.obs_group_dict.update(dict([(observation, "group_rain") for observation in _rain_amount_fields]))

# Define unit group 'group_rate'
weewx.units.USUnits['group_rate'] = 'per_hour'
weewx.units.MetricUnits['group_rate'] = 'per_hour'
weewx.units.MetricWXUnits['group_rate'] = 'per_hour'

weewx.units.default_unit_format_dict['per_hour'] = '%.0f'
weewx.units.default_unit_label_dict['per_hour'] = ' per hour'


def loader(config_dict, engine):
    return WeatherlinkLiveDriver(config_dict, engine)


def confeditor_loader():
    return WeatherlinkLiveConfEditor()


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
        self.wind_service = WllWindGustService(engine, conf_dict, self.mappers, self.configuration.log_success,
                                               self.configuration.log_error)

        self.is_running = False
        self.scheduler = None
        self.no_data_count = 0
        self.data_event = None
        self.poll_host = None
        self.push_host = None

    @property
    def hardware_name(self):
        """Name of driver"""
        return DRIVER_NAME

    def genLoopPackets(self):
        """Open connection and generate loop packets"""

        if not self.is_running:
            try:
                self.start()
            except Exception as e:
                raise InitializationError("Error while starting driver: %s" % str(e)) from e

        # Either it's the first iteration of the driver
        # or we've just returned a packet and are now resuming the driver.
        self._reset_data_count()

        self._log_success("Entering driver loop")
        while True:
            self._check_no_data_count()

            try:
                self.scheduler.raise_error()
                self.poll_host.raise_error()
                self.push_host.raise_error()
            except Exception as e:
                raise WeeWxIOError("Error while receiving or processing packets: %s" % str(e)) from e

            log.debug("Waiting for new packet")
            self.data_event.wait(5)  # do a check every 5 secs
            self.data_event.clear()

            if self.poll_host.packets:
                self._log_success("Emitting poll packet")
                self._reset_data_count()
                yield self.poll_host.packets.popleft()

            elif self.push_host.packets:
                self._log_success("Emitting push (broadcast) packet")
                self._reset_data_count()
                yield self.push_host.packets.popleft()

            else:
                self._increase_no_data_count()

    def start(self):
        if self.is_running:
            return

        self.is_running = True
        self.data_event = threading.Event()
        self.poll_host = data_host.WllPollHost(
            self.configuration.host,
            self.mappers,
            self.data_event,
            self.configuration.socket_timeout
        )
        self.push_host = data_host.WLLBroadcastHost(
            self.configuration.host,
            self.mappers,
            self.data_event,
            self.configuration.socket_timeout
        )
        self.scheduler = scheduler.Scheduler(
            self.configuration.polling_interval,
            self.poll_host.poll,
            self.push_host.refresh_broadcast,
            self.data_event
        )

    def closePort(self):
        """Close connection"""

        self.is_running = False
        if self.scheduler is not None:
            self.scheduler.cancel()
        if self.poll_host is not None:
            self.poll_host.close()
        if self.push_host is not None:
            self.push_host.close()

    def _increase_no_data_count(self):
        self.no_data_count += 1
        self._log_failure("No data since %d iterations" % self.no_data_count, logging.WARNING)

    def _reset_data_count(self):
        self.no_data_count = 0

    def _check_no_data_count(self):
        max_iterations = self.configuration.max_no_data_iterations
        if max_iterations < 1:
            raise ValueError("Max iterations without data must not be less than 1 (got: %d)" % max_iterations)

        if self.no_data_count >= max_iterations:
            raise WeeWxIOError("Received no data for %d iterations" % max_iterations)

    def _log_success(self, msg: str, level: int = logging.DEBUG) -> None:
        if not self.configuration.log_success:
            return
        log.log(level, msg)

    def _log_failure(self, msg: str, level: int = logging.DEBUG) -> None:
        if not self.configuration.log_error:
            return
        log.log(level, msg)


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
    mapping = th:1, th_indoor, baro, rain:1, wind:1, thw:1, windchill:1
"""

    def modify_config(self, config_dict):
        print("""
Configuring accumulators for custom types.""")
        config_dict.setdefault('Accumulator', {})

        config_dict['Accumulator'].setdefault('rainCount', {})
        config_dict['Accumulator']['rainCount']['extractor'] = 'sum'

        config_dict['Accumulator'].setdefault('rainSize', {})
        config_dict['Accumulator']['rainSize']['extractor'] = 'last'
