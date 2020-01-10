import logging
import random
import threading
from collections import deque
from typing import List

import weewx
from user.weatherlink_live import davis_http
from user.weatherlink_live.callback import PacketCallback
from user.weatherlink_live.davis_broadcast import WllBroadcastReceiver
from user.weatherlink_live.mappers import AbstractMapping
from user.weatherlink_live.packets import DavisConditionsPacket

log = logging.getLogger(__name__)


class DataHost(object):
    """Base host class for polled as well as broadcasted data"""

    def __init__(self, mappers: List[AbstractMapping]):
        self._mappers = mappers

        self.packets = deque()
        self.error = None

    @property
    def has_error(self):
        return self.error is not None

    def raise_error(self):
        if self.has_error:
            raise self.error

    def _create_record(self, packet: DavisConditionsPacket):
        record = dict()

        for mapper in self._mappers:
            mapper.map(packet, record)
        self.packets.append(record)

        record['dateTime'] = packet.timestamp
        record['usUnits'] = weewx.US


class WllPollHost(DataHost):
    """Host object for polling data from WLL"""

    def __init__(self, host: str, polling_interval: float, mappers: List[AbstractMapping]):
        super().__init__(mappers)
        self.host = host
        self.polling_interval = polling_interval

        if polling_interval < 10:
            raise ValueError("Polling interval shouldn't be less than 10 )got: %d)" % polling_interval)

        self._timer = threading.Timer(interval=self.polling_interval * random.random(), function=self._reschedule)
        self._timer.start()

    def _poll(self):
        packet = davis_http.request_current(self.host)
        log.debug("Polled current conditions")

        self._create_record(packet)

    def _reschedule(self):
        try:
            self._poll()
        except Exception as e:
            self.error = e
            log.error("Error occurred. Don't reschedule")
            return

        if self._timer is not None:
            self._timer.cancel()
        log.debug("Next poll in %f secs" % self.polling_interval)
        self._timer = threading.Timer(interval=self.polling_interval, function=self._reschedule)
        self._timer.start()

    def close(self):
        if self._timer is not None:
            self._timer.cancel()


class WLLBroadcastHost(DataHost, PacketCallback):
    """Class for triggering UDP broadcasts and receiving them"""

    def __init__(self, host: str, mappers: List[AbstractMapping]):
        super().__init__(mappers)
        self.host = host

        self._receiver = None
        self._timer = None
        self._port = 22222

        self._timer = threading.Timer(interval=10 * random.random(), function=self._reschedule)
        self._timer.start()

    def _reschedule(self):
        log.debug("Re-requesting UDP broadcast")
        packet = davis_http.start_broadcast(self.host, 300)
        duration = packet.duration
        port = packet.broadcast_port

        if self._port != port:
            log.info("Broadcast port changed from %s to %s" % (self._port, port))
            self._port = port

        log.debug("Restarting broadcast reception")
        self._stop_broadcast_reception()
        self._start_broadcast_reception()

        if self._timer is not None:
            self._timer.cancel()

        reschedule_duration = self._reschedule_duration(duration)
        log.debug("Next broadcast reschedule in %d seconds" % reschedule_duration)

        self._timer = threading.Timer(reschedule_duration, function=self._reschedule)
        self._timer.start()

    @staticmethod
    def _reschedule_duration(actual_duration: int) -> int:
        if actual_duration < 10:
            return 1
        elif actual_duration < 60:
            return actual_duration - 10
        else:
            return actual_duration - 30

    def _start_broadcast_reception(self):
        self._receiver = WllBroadcastReceiver(self.host, self._port, self)

    def _stop_broadcast_reception(self):
        if self._receiver is None:
            return
        self._receiver.close()

    def on_packet_received(self, packet: DavisConditionsPacket):
        log.debug("Received new broadcast packet")
        try:
            self._create_record(packet)
        except Exception as e:
            self.error = e
            self.close()

    def on_packet_receive_error(self, e: BaseException):
        self.error = e
        self.close()

    def close(self):
        if self._timer is not None:
            self._timer.cancel()
        self._stop_broadcast_reception()
