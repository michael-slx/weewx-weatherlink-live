# Copyright © 2020-2025 Michael Schantl and contributors
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
import time
from typing import Optional

import requests

from user.weatherlink_live.packets import WlHttpBroadcastStartRequestPacket, WlHttpConditionsRequestPacket
from weewx import WeeWxIOError

log = logging.getLogger(__name__)


def start_broadcast(host: str, duration, timeout: float = 5):
    error: Optional[Exception] = None

    for i in range(3):
        try:
            r = requests.get("http://%s:80/v1/real_time?duration=%d" % (host, duration), timeout=timeout)
            json = r.json()
            broadcast_start_packet = WlHttpBroadcastStartRequestPacket.try_create(json, host)

            if i > 0:
                log.error("Successfully sent broadcast start request after %d attempts" % (i + 1))
            else:
                log.debug("Sent broadcast start request")

            return broadcast_start_packet
        except Exception as e:
            error = e
            log.error(e)
            log.error("HTTP broadcast start request failed. Retry #%d follows shortly" % (i + 1))
        time.sleep(2.5)

    if error is not None:
        raise error

    raise WeeWxIOError("HTTP broadcast start request failed without setting an error")


def request_current(host: str, timeout: float = 5):
    error: Optional[Exception] = None

    for i in range(3):
        try:
            r = requests.get("http://%s:80/v1/current_conditions" % host, timeout=timeout)
            json = r.json()
            conditions_packet = WlHttpConditionsRequestPacket.try_create(json, host)

            if i > 0:
                log.error("Successfully sent conditions request after %d attempts" % (i + 1))
            else:
                log.debug("Sent conditions request")

            return conditions_packet
        except Exception as e:
            error = e
            log.error(e)
            log.error("HTTP conditions request failed. Retry #%d follows shortly" % (i + 1))
        time.sleep(2.5)

    if error is not None:
        raise error

    raise WeeWxIOError("HTTP conditions request failed without setting an error")
