import json
import logging
import threading
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SHUT_RD

from user.weatherlink_live.callback import PacketCallback
from user.weatherlink_live.packets import WlUdpBroadcastPacket

log = logging.getLogger(__name__)


class WllBroadcastReceiver(object):
    """Receive UDP broadcasts from WeatherLink Live"""

    def __init__(self, broadcasting_wl_host: str, port: int, callback: PacketCallback):
        self.broadcasting_wl_host = broadcasting_wl_host
        self.port = port
        self.callback = callback

        self.sock = None

        self.stop_signal = threading.Event()
        self.thread = threading.Thread(name='WLL-BroadcastReception', target=self._reception)
        self.thread.start()

    def _reception(self):
        try:
            self.sock = socket(AF_INET, SOCK_DGRAM)
            self.sock.bind(('', self.port))
            self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

            while not self.stop_signal.is_set():
                data, source_addr = self.sock.recvfrom(2048)
                json_data = json.loads(data.decode("utf-8"))

                packet = WlUdpBroadcastPacket.try_create(json_data, self.broadcasting_wl_host)
                self.callback.on_packet_received(packet)

            self.sock.close()
        except Exception as e:
            self.callback.on_packet_receive_error(e)
            raise e

    def close(self):
        self.stop_signal.set()
        if self.sock is not None:
            self.sock.shutdown(SHUT_RD)
            self.sock.close()
            self.sock = None
        self.thread.join(10)
