import logging
import threading

from user.weatherlink_live import data_host, scheduler
from user.weatherlink_live.configuration import create_configuration
from user.weatherlink_live.service import WllWindGustService
from user.weatherlink_live.static.version import DRIVER_NAME, DRIVER_VERSION
from weewx import WeeWxIOError
from weewx.drivers import AbstractDevice
from weewx.engine import InitializationError

log = logging.getLogger(__name__)


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
        # or we've just created an archive packet and are
        # now resuming the driver.
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

            emitted_poll_packet = False
            emitted_push_packet = False

            while self.poll_host.packets:
                self._log_success("Emitting poll packet")
                self._reset_data_count()
                emitted_poll_packet = True
                yield self.poll_host.packets.popleft()

            while self.push_host.packets:
                self._log_success("Emitting push (broadcast) packet")
                self._reset_data_count()
                emitted_push_packet = True
                yield self.push_host.packets.popleft()

            if not emitted_poll_packet and not emitted_push_packet:
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
