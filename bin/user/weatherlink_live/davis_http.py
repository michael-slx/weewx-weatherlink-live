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
            return WlHttpBroadcastStartRequestPacket.try_create(json, host)
        except Exception as e:
            error = e
            log.error(e)
            log.error("HTTP broadcast start request failed. Retry #%d follows shortly" % i)
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
            return WlHttpConditionsRequestPacket.try_create(json, host)
        except Exception as e:
            error = e
            log.error(e)
            log.error("HTTP conditions request failed. Retry #%d follows shortly" % i)
        time.sleep(2.5)

    if error is not None:
        raise error

    raise WeeWxIOError("HTTP conditions request failed without setting an error")
