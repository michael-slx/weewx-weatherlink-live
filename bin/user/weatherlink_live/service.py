import logging
from typing import List, Dict

import weewx
from user.weatherlink_live.mappers import AbstractMapping, WindGustMapping
from weewx.engine import StdService

log = logging.getLogger(__name__)


class WllWindService(StdService):
    """Service for calculating ARCHIVE records from LOOP wind measurements"""

    def __init__(self, engine, config_dict, mappers: List[AbstractMapping], log_success: bool = False,
                 log_failure: bool = True):
        super().__init__(engine, config_dict)

        self.mappers = mappers
        self.log_success = log_success
        self.log_failure = log_failure

        self.map_targets = self._extract_map_sources()
        self._log_success("Found %d wind mappings" % len(self.map_targets))
        if len(self.map_targets) < 1:
            self._log_failure("No wind mappings available. Aborting service.")
            return

        self._clear()

        self.bind(weewx.STARTUP, self.startup)
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        self.bind(weewx.END_ARCHIVE_PERIOD, self.end_archive_period)

    def _log_success(self, message: str, level: int = logging.DEBUG):
        if not self.log_success:
            return
        log.log(level, "%s: %s" % (type(self).__name__, message))

    def _log_failure(self, message: str, level: int = logging.ERROR):
        if not self.log_failure:
            return
        log.log(level, "%s: %s" % (type(self).__name__, message))

    def _extract_map_sources(self) -> List[Dict[str, str]]:
        return [mapper.targets for mapper in self.mappers if isinstance(mapper, WindGustMapping)]

    def _clear(self):
        self._log_success("Clearing max gust values")
        self.max_loop_gust = dict()

    def startup(self, event):
        self._log_success("Service startup")
        self._clear()

    def new_loop_packet(self, event):
        record = event.packet

        for wind_mapping in self.map_targets:
            k_wind_dir = wind_mapping['wind_dir']
            k_wind_speed = wind_mapping['wind_speed']
            k_gust_dir = wind_mapping['gust_dir']
            k_gust_speed = wind_mapping['gust_speed']

            if k_wind_dir not in record or k_wind_speed not in record:
                self._log_success("Wind observations %s:%s not in record" % (k_wind_speed, k_wind_dir))  # not an error
                continue

            current_speed = record[k_wind_speed]
            current_dir = record[k_wind_dir]

            max_gust_speed = self.max_loop_gust.get(k_gust_speed, 0.0)
            max_gust_dir = self.max_loop_gust.get(k_gust_dir, None)

            if max_gust_dir is None or current_speed >= max_gust_speed:
                self._log_success("New wind vector %.02f:%s larger than %.02f:%s" % (
                current_speed, current_dir, max_gust_speed, max_gust_dir))
                self.max_loop_gust[k_gust_speed] = current_speed
                self.max_loop_gust[k_gust_dir] = current_dir

            self._log_success("Updating record with dict: %s" % repr(self.max_loop_gust))
            record.update(self.max_loop_gust)

    def end_archive_period(self, event):
        self._log_success("End of archive period")
        self._clear()
