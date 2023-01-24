# Copyright © 2020-2021 Michael Schantl and contributors
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
import sched
import threading
import time
from datetime import datetime
from math import floor
from typing import Optional, Callable

POLL_INTERVAL_MIN = 10.0
POLL_INTERVAL_MAX = 300.0
PUSH_REFRESH_INTERVAL = 1200.0  # Refresh broadcast every 20 minutes
PUSH_DURATION = PUSH_REFRESH_INTERVAL + 300.0  # Request broadcast for interval + 5 minutes

log = logging.getLogger(__name__)


def _format_iso(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S Z')


class Scheduler(object):
    """Centrally schedule HTTP requests to avoid overloading server"""

    def __init__(self, polling_interval: float, poll_callback: Callable[[], None],
                 push_refresh_callback: Callable[[float], None], data_event: threading.Event):

        self.polling_interval = polling_interval
        if polling_interval < POLL_INTERVAL_MIN:
            raise ValueError(
                "Polling interval shouldn't be less than %d )got: %d)" % (POLL_INTERVAL_MIN, polling_interval))
        elif polling_interval > POLL_INTERVAL_MAX:
            raise ValueError(
                "Polling interval shouldn't be more than %d )got: %d)" % (POLL_INTERVAL_MAX, polling_interval))

        if poll_callback:
            self._poll_callback = poll_callback
        else:
            self._poll_callback = None
            self.polling_interval = PUSH_REFRESH_INTERVAL

        self._push_refresh_callback = push_refresh_callback
        self.data_event = data_event

        self.error = None

        self._push_refresh_tick_count = floor(PUSH_REFRESH_INTERVAL / self.polling_interval)
        self._push_refresh_ticks = self._push_refresh_tick_count
        log.debug("Push refresh will happen every %d scheduler ticks" % self._push_refresh_tick_count)

        self._tick_task_id = None

        self._scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)

        self._run = True
        self._scheduler_thread = threading.Thread(target=self._run_scheduler)
        self._scheduler_thread.setName("WLL-HTTP-Scheduler")
        self._scheduler_thread.setDaemon(True)
        self._scheduler_thread.start()

        self._scheduler_tick()

    @property
    def has_error(self) -> bool:
        return self.error is not None

    def raise_error(self):
        if not self.has_error:
            return
        raise self.error

    def _notify_error(self, e: BaseException):
        self.error = e
        self.data_event.set()

    def _run_scheduler(self):
        while self._run:
            self._scheduler.run(blocking=True)

    def _scheduler_tick(self):
        log.debug("Scheduler tick")

        try:
            self._do_tick()
        except BaseException as e:
            log.error("Error caught in scheduler tick. Not rescheduling")
            self._notify_error(e)
            return

        next_tick_abs_time = time.time() + self.polling_interval
        log.debug("Next scheduler tick at %s" % _format_iso(next_tick_abs_time))
        self._tick_task_id = self._scheduler.enterabs(next_tick_abs_time, 0, self._scheduler_tick)

    def _do_tick(self):
        log.debug("Notifying poll callback")
        if self._poll_callback:
            self._poll_callback()

        if self._push_refresh_ticks >= self._push_refresh_tick_count:
            log.debug("Notifying push refresh callback")
            self._push_refresh_callback(PUSH_DURATION)
            self._push_refresh_ticks = 0

        self._push_refresh_ticks += 1
        log.debug(
            "%d scheduler ticks until next push refresh" % (self._push_refresh_tick_count - self._push_refresh_ticks))

    def cancel(self):
        log.debug("Cancelling scheduler")
        self._run = False

        if self._tick_task_id is not None:
            log.debug("Cancelling tick task")
            try:
                self._scheduler.cancel(self._tick_task_id)
            except ValueError:
                pass

        if not self._scheduler.empty():
            raise ValueError("Scheduler did not cancel all task")

        self._scheduler_thread.join(30)
        log.info("All tasks cancelled")
