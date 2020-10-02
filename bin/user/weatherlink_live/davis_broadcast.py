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

import json
import logging
import select
import threading
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR

from user.weatherlink_live.callback import PacketCallback
from user.weatherlink_live.packets import WlUdpBroadcastPacket
from weewx import WeeWxIOError

log = logging.getLogger(__name__)


class WllBroadcastReceiver(object):
    """Receive UDP broadcasts from WeatherLink Live"""

    def __init__(self, broadcasting_wl_host: str, port: int, callback: PacketCallback):
        self.broadcasting_wl_host = broadcasting_wl_host
        self.port = port
        self.callback = callback

        self.wait_timeout = 5

        self.sock = None

        self.stop_signal = threading.Event()
        self.thread = threading.Thread(name='WLL-BroadcastReception', target=self._reception)
        self.thread.start()

    def _reception(self):
        log.debug("Starting broadcast reception")
        try:
            self.sock = socket(AF_INET, SOCK_DGRAM)
            self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            self.sock.bind(('', self.port))

            while not self.stop_signal.is_set():
                r, _, _ = select.select([self.sock], [], [], self.wait_timeout)
                if not r:
                    continue

                data, source_addr = self.sock.recvfrom(2048)
                try:
                    json_data = json.loads(data.decode("utf-8"))
                except JSONDecodeError as e:
                    raise WeeWxIOError("Error decoding broadcast packet JSON") from e

                packet = WlUdpBroadcastPacket.try_create(json_data, self.broadcasting_wl_host)
                self.callback.on_packet_received(packet)

        except Exception as e:
            self.callback.on_packet_receive_error(e)
            raise e

    def close(self):
        log.debug("Stopping broadcast reception")
        self.stop_signal.set()
        self.thread.join(self.wait_timeout * 3)

        if self.thread.is_alive():
            log.warn("Broadcast reception thread still alive. Force closing socket")

        if self.sock is not None:
            self.sock.close()
            self.sock = None
            log.debug("Closed broadcast receiving socket")

        log.debug("Stopped broadcast reception")
