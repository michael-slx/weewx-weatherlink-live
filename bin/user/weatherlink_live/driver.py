# Copyright © 2020-2024 Michael Schantl and contributors
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

import logging
import threading

from user.weatherlink_live import data_host, scheduler
from user.weatherlink_live.configuration import create_configuration
from user.weatherlink_live.service import WllService
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
        self.service = WllService(engine, conf_dict, self.mappers, self.configuration.log_success,
                                  self.configuration.log_error)

        self.is_running = False
        self.scheduler = None
        self.no_data_count = 0
        self.data_event = None
        self.poll_host = None
        self.wlcom_host = None
        self.push_host = None
        self.archive_interval_ = 1 # In minutes. It can be 1, 5, 10, 15, 30, 60 or 120

    @property
    def hardware_name(self):
        """Name of driver"""
        return DRIVER_NAME

    @property
    def archive_interval(self):
        return self.archive_interval_ * 60

    def genArchiveRecords(self, since_ts):
        if not self.is_running:
            try:
                self.start()
            except Exception as e:
                raise InitializationError("Error while starting driver: %s" % str(e)) from e

        if self.wlcom_host:
            while self.wlcom_host.packets:
                if since_ts and self.wlcom_host.packets[0]['dateTime'] <= since_ts:
                    # Ack unwanted archive packet
                    self.wlcom_host._receiver.ack_packet(self.wlcom_host.packets.popleft()['dateTime'], False)
                    continue

                self._log_success("Emitting wlcom packet")
                self._reset_data_count()
                self.wlcom_host.packets[0]['interval'] = self.archive_interval_
                yield self.wlcom_host.packets.popleft()

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
                if self.configuration.use_wlcom:
                    self.wlcom_host.raise_error()
                self.push_host.raise_error()
            except Exception as e:
                raise WeeWxIOError("Error while receiving or processing packets: %s" % repr(e)) from e

            log.debug("Waiting for new packet")
            self.data_event.wait(5)  # do a check every 5 secs
            self.data_event.clear()

            emitted_poll_packet = False
            emitted_push_packet = False

            while self.poll_host.packets:
                self._log_success("Emitting poll packet", level=logging.INFO)
                self._reset_data_count()
                emitted_poll_packet = True
                yield self.poll_host.packets.popleft()

            while self.push_host.packets:
                self._log_success("Emitting push (broadcast) packet", level=logging.INFO)
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
        if self.configuration.use_wlcom:
            self.wlcom_host = data_host.WLLWlcomHost(
                self.archive_interval_,
                self.service,
                self.mappers,
                self.poll_host.txid,
                self.data_event,
                self.configuration.socket_timeout
            )

    @property
    def archive_interval(self):
        raise NotImplementedError("Not supported")

    def genArchiveRecords(self, _):
        raise NotImplementedError("Not supported")

    def getTime(self):
        raise NotImplementedError("Not supported")

    def setTime(self):
        raise NotImplementedError("Not supported")

    def closePort(self):
        """Close connection"""

        self.is_running = False
        if self.scheduler is not None:
            self.scheduler.cancel()
        if self.poll_host is not None:
            self.poll_host.close()
        if self.wlcom_host is not None:
            self.wlcom_host.close()
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
