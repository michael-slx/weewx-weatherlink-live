# Copyright © 2020-2023 Michael Schantl and contributors
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

import time
from typing import Optional

import weewx
from user.weatherlink_live import configuration, davis_http, cli, davis_broadcast, callback
from user.weatherlink_live.packets import DavisConditionsPacket


def test_http(config: configuration.Configuration) -> None:
    print(
        f"{cli.Colors.STANDOUT}{cli.Colors.HEADER}Trying to request current conditions from WeatherLink Live \"%s\"{cli.Colors.END}" % config.host)

    for i in range(10):
        print(f"Request %2d ... " % (i + 1), end="", flush=True)
        _request_http_conditions(config)
        print(f"{cli.Colors.OK}OK!{cli.Colors.END}", flush=True)
        time.sleep(1)

    print(
        f"{cli.Colors.STANDOUT}{cli.Colors.OK}Successfully requested current conditions from WeatherLink Live \"%s\"!{cli.Colors.END}" % config.host)


def _request_http_conditions(config):
    current_conditions = davis_http.request_current(config.host, config.socket_timeout)
    current_conditions.raise_error()
    if len(current_conditions.tx_list) < 1:
        raise weewx.WeeWxIOError("No transmitters in current conditions record")


def test_udp(config: configuration.Configuration) -> None:
    port = _request_broadcast_activation(config, 120)
    _listen_for_broadcasts(config, port, 60, 2.66)


def _request_broadcast_activation(config: configuration.Configuration, duration: int) -> int:
    print(f"Enabling live data from WeatherLink Live \"%s\" for %d seconds" % (config.host, duration))
    broadcast_request = davis_http.start_broadcast(config.host, duration, config.socket_timeout)
    broadcast_request.raise_error()
    print(
        f"Enabled live data from WeatherLink Live \"%s\" for %d seconds on port %s\n" % (
            config.host, broadcast_request.duration, str(broadcast_request.broadcast_port)))
    return broadcast_request.broadcast_port


def _listen_for_broadcasts(config: configuration.Configuration, port: int, duration: int,
                           max_avg_interval: float) -> None:
    print(
        f"{cli.Colors.STANDOUT}{cli.Colors.HEADER}Trying to receive live data from WeatherLink Live \"%s\" on port %s for %d seconds{cli.Colors.END}" % (
            config.host, str(port), duration))

    test_callback: TestPacketCallback = TestPacketCallback()
    receiver = davis_broadcast.WllBroadcastReceiver(config.host, port, test_callback)
    time.sleep(duration)
    receiver.close()

    last_error = test_callback.last_error
    if last_error is not None:
        raise last_error

    if test_callback.packet_count < 1:
        raise weewx.WeeWxIOError("No live data packets were received from WeatherLink Live \"%s\"" % config.host)

    avg_packet_interval = (duration * 1.0) / test_callback.packet_count

    if avg_packet_interval <= max_avg_interval:
        print(
            f"{cli.Colors.STANDOUT}{cli.Colors.OK}Successfully received %d live data packets (interval: %0.3f s) from WeatherLink Live \"%s\" on port %s{cli.Colors.END}" % (
                test_callback.packet_count, avg_packet_interval, config.host, str(port)))

    else:
        raise weewx.WeeWxIOError(
            "Received %d live data packet(s) from WeatherLink Live \"%s\" (interval is only %0.3f s)" % (
                test_callback.packet_count, config.host, avg_packet_interval))


class TestPacketCallback(callback.PacketCallback):

    def __init__(self):
        super().__init__()

        self.packet_count: int = 0
        self.last_error: Optional[BaseException] = None

    def on_packet_received(self, packet: DavisConditionsPacket):
        packet.raise_error()

        if len(packet.tx_list) < 1:
            raise weewx.WeeWxIOError("No transmitters in live data record")

        self.packet_count += 1
        print("Received %2d packet(s) ..." % self.packet_count)

    def on_packet_receive_error(self, e: BaseException):
        self.last_error = e
