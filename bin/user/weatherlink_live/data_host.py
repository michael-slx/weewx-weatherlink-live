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
from collections import deque
from typing import List

import weewx
from user.weatherlink_live.callback import PacketCallback
from user.weatherlink_live.davis_broadcast import WllBroadcastReceiver
from user.weatherlink_live.davis_http import start_broadcast, request_current
from user.weatherlink_live.davis_wlcom import WllWlcomReceiver
from user.weatherlink_live.mappers import AbstractMapping
from user.weatherlink_live.packets import DavisConditionsPacket
from user.weatherlink_live.service import WllService

log = logging.getLogger(__name__)


class DataHost(object):
    """Base host class for polled as well as broadcasted data"""

    def __init__(self, mappers: List[AbstractMapping], data_event: threading.Event):
        self._mappers = mappers
        self._data_event = data_event

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

        self._data_event.set()

    def notify_error(self, e):
        self.error = e
        self._data_event.set()


class WllPollHost(DataHost):
    """Host object for polling data from WLL"""

    def __init__(self,
                 host: str,
                 mappers: List[AbstractMapping],
                 data_event: threading.Event,
                 http_timeout: float = 20):
        super().__init__(mappers, data_event)
        self.host = host
        self.http_timeout = http_timeout
        self.txid = dict()

    def poll(self):
        packet = request_current(self.host, timeout=self.http_timeout)
        log.debug("Polled current conditions")

        for ls in packet._conditions:
            if 'txid' in ls:
                self.txid[ls['lsid']] = ls['txid']

        self._create_record(packet)

    def close(self):
        pass


class WLLBroadcastHost(DataHost, PacketCallback):
    """Class for triggering UDP broadcasts and receiving them"""

    def __init__(self,
                 host: str,
                 mappers: List[AbstractMapping],
                 data_event: threading.Event,
                 http_timeout: float = 20):
        super().__init__(mappers, data_event)
        self.host = host
        self.http_timeout = http_timeout

        self._receiver = None
        self._port = 22222

    def refresh_broadcast(self, request_duration: float):
        log.debug("Re-requesting UDP broadcast")
        packet = start_broadcast(self.host, request_duration, timeout=self.http_timeout)
        port = packet.broadcast_port

        if self._port != port:
            log.info("Broadcast port changed from %s to %s" % (self._port, port))
            self._port = port

        log.debug("Restarting broadcast reception")
        self._stop_broadcast_reception()
        self._start_broadcast_reception()

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
            self.notify_error(e)
            self.close()

    def on_packet_receive_error(self, e: BaseException):
        self.notify_error(e)
        self.close()

    def close(self):
        self._stop_broadcast_reception()


class WLLWlcomHost(DataHost, PacketCallback):
    """Class for capturing wl.com traffic"""

    def __init__(self,
                 archive_interval: int,
                 service: WllService, 
                 mappers: List[AbstractMapping],
                 txid: dict,
                 data_event: threading.Event,
                 http_timeout: float = 20):
        super().__init__(mappers, data_event)
        self.archive_interval = archive_interval
        self.http_timeout = http_timeout
        self.txid = txid

        self._port = 5621
        self._receiver = WllWlcomReceiver(archive_interval, service, self._port, self)

    def _stop_wlcom_reception(self):
        if self._receiver is None:
            return
        self._receiver.close()

    def on_packet_received(self, packet: DavisConditionsPacket):
        log.debug("Received new wlcom packet")
        try:
            record = dict()

            for mapper in self._mappers:
                mapper.map(packet, record)

            record['dateTime'] = packet.timestamp
            record['usUnits'] = weewx.US

            self.packets.append(record)
            # Don't signal the Loop generator here
        except Exception as e:
            self.notify_error(e)
            self.close()

    def on_packet_receive_error(self, e: BaseException):
        self.notify_error(e)
        self.close()

    def close(self):
        self._stop_wlcom_reception()
