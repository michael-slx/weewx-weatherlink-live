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

import logging
import sched
import threading
import time
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)


def _format_iso(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S Z')


class Scheduler(object):
    """Centrally schedule HTTP requests to avoid overloading server"""

    def __init__(self):
        self._scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)

        self._poll_task_id = None
        self._push_refresh_task_id = None

        self._run = True
        self._scheduler_thread = threading.Thread(target=self._run_scheduler)
        self._scheduler_thread.setName("WLL-HTTP-Scheduler")
        self._scheduler_thread.setDaemon(True)
        self._scheduler_thread.start()

    def _run_scheduler(self):
        while self._run:
            self._scheduler.run(blocking=True)

    def add_poll_task(self, abs_time: float, func: callable):
        log.debug("Adding poll task at %s" % _format_iso(abs_time))
        self._poll_task_id = self._scheduler.enterabs(abs_time, 10, func)

    def add_push_refresh_task(self, abs_time: float, func: callable):
        log.debug("Adding push refresh task at %s" % _format_iso(abs_time))
        self._push_refresh_task_id = self._scheduler.enterabs(abs_time, 5, func)

    def cancel(self):
        log.debug("Cancelling all tasks")

        self._run = False

        if self._poll_task_id is None:
            self._scheduler.cancel(self._poll_task_id)
        if self._push_refresh_task_id is None:
            self._scheduler.cancel(self._push_refresh_task_id)

        if not self._scheduler.empty():
            raise ValueError("Scheduler did not cancel all task")

        self._scheduler_thread.join(30)

        log.info("All tasks cancelled")
