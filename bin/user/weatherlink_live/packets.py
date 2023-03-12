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

"""
Packets as returned by the API
"""
import logging
from typing import Optional, Any, List, Dict, Set, Tuple

import weewx
from user.weatherlink_live.static import PacketSource
from user.weatherlink_live.static.packets import DataStructureType

log = logging.getLogger(__name__)

TxEntry = Dict[str, Optional[Any]]
ConditionSet = List[TxEntry]
TxList = List[Tuple[DataStructureType, int | None]]


class NotInPacket(Exception):
    """
    Raised by mapping to signal that wanted observation isn't in the packet
    """
    pass


class DavisPacket(object):
    """A packet as returned by WeatherLinkLive/AirLink APIs"""

    def __init__(self, packet: dict, host: str):
        self.host = host

        error = packet.get('error', {})
        self.error_code = error.get('code') if error is not None else None
        self.error_message = error.get('message') if error is not None else None

    @property
    def has_error(self):
        return self.error_code is not None or self.error_message is not None

    def raise_error(self):
        if self.has_error:
            raise weewx.WeeWxIOError(
                "Device %s returned error %d: %s" % (self.host, self.error_code, self.error_message)
            )


class DavisConditionsPacket(DavisPacket):
    """Interface for packets holding actual data"""

    @property
    def timestamp(self) -> int:
        """Return timestamp of packet"""
        raise NotImplementedError("Abstract type")

    @property
    def _conditions(self) -> ConditionSet:
        """Return list of dictionaries with observations"""
        raise NotImplementedError("Abstract type")

    @property
    def data_source(self) -> PacketSource:
        """Returns source of data"""
        raise NotImplementedError("Abstract type")

    def get_observation(self, observation: str, dst: DataStructureType = None, tx: int = None) -> Optional[Any]:
        """
        Find the value of an observation in this packet

        When enforce_unique is set to true, a ValueError is raised if the combination of dst and tx does not result in an unique sensor.

        :param observation: name of the requested observation
        :param dst: data structure type for filtering
        :param tx: transmitter (tx) id for filtering
        :return: value of requested observation
        :raise NotInPacket: signals that the observation wasn't found
        """

        filtered = self._find_tx_entry(dst, tx)

        if len(filtered) < 1 or observation not in filtered[0]:
            raise NotInPacket("Observation %s not found in packet of type %s" % (observation, type(self).__name__))

        return filtered[0][observation]

    def _find_tx_entry(self,
                       tx_type: DataStructureType = None,
                       tx_id: int = None) -> Optional[TxEntry]:
        filtered = self._conditions
        if tx_type is not None:
            filtered = [conditions for conditions in filtered if conditions.get('data_structure_type') == tx_type]
        if tx_id is not None:
            filtered = [conditions for conditions in filtered if conditions.get('txid') == tx_id]
        if len(filtered) > 1:
            raise ValueError(
                "Combination of dst %s and tx id %s did not result in an unique sensor" % (str(tx_type), str(tx_id)))
        return filtered[0] if len(filtered) >= 1 else None

    def get_observation_from_multiple(self, combinations: List[dict]):
        """
        Attempt to fetch the observation from the given combinations of observation, dst and tx id

        The dictionaries are passed as kwargs to the get_observation, so look there for naming of keys.

        :param combinations: a list of dictionaries with combinations
        :return: value of observation
        :raise NotInPacket: signals that the observation wasn't found using any combination
        """

        for combination in combinations:
            try:
                return self.get_observation(**combination)
            except NotInPacket:
                pass

        raise NotInPacket("Could not find observation using combinations %s" % repr(combinations))

    @property
    def tx_list(self) -> TxList:
        """
        Get a list of available TX type/id combinations
        :return: List of TX type/id tuples
        """
        return [(tx_entry['data_structure_type'], tx_entry.get('txid')) for tx_entry in self._conditions]

    def has_observation_values(self,
                               observation_names: Set[str],
                               tx_type: Optional[DataStructureType] = None,
                               tx_id: Optional[int] = None) -> bool:
        """
        Check whether an observation exists and has a value

        :param observation_names: Set of observation names (keys) to be checked
        :param tx_type: Type of transmitter to check
        :param tx_id: Id of transmitter to check
        :return: `true` if all observations exist for the specified transmitter; `false` otherwise
        :raise ValueError: if the given combination of tx type and id is not unique
                """

        tx_entry = self._find_tx_entry(tx_type, tx_id)
        if not tx_entry:
            raise ValueError("TX type %s and id %s did not match any entry" % (repr(tx_type), repr(tx_id)))

        for observation_key in observation_names:
            if observation_key not in tx_entry.keys():
                return False

        return True


class WlHttpConditionsRequestPacket(DavisConditionsPacket):
    """Packet returned by WeatherLinkLive 'current_conditions' endpoint"""

    def __init__(self, packet: dict, host: str):
        super().__init__(packet, host)
        self.raise_error()

        self.device_id = packet['data']['did']
        self._timestamp = packet['data']['ts']
        self.conditions = packet['data']['conditions']

    @staticmethod
    def try_create(packet: dict, host: str):
        log.debug("Trying to create HTTP conditions packet")
        try:
            return WlHttpConditionsRequestPacket(packet, host)
        except (ValueError, KeyError) as e:
            raise weewx.WeeWxIOError("Could not extract main entries of packet") from e

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def _conditions(self) -> dict:
        return self.conditions

    @property
    def data_source(self) -> PacketSource:
        return PacketSource.WEATHER_POLL


class WlHttpBroadcastStartRequestPacket(DavisPacket):
    """Packet returned by WeatherLinkLive 'real_time' endpoint"""

    def __init__(self, packet: dict, host: str):
        super().__init__(packet, host)
        self.raise_error()

        self.broadcast_port = packet['data']['broadcast_port']
        self.duration = packet['data']['duration']

    @staticmethod
    def try_create(packet: dict, host: str):
        try:
            return WlHttpBroadcastStartRequestPacket(packet, host)
        except (ValueError, KeyError) as e:
            raise weewx.WeeWxIOError("Could not extract main entries of packet") from e


class WlUdpBroadcastPacket(DavisConditionsPacket):
    """Packet as broadcasted over UDP"""

    def __init__(self, packet: dict, host: str):
        super().__init__(packet, host)
        self.raise_error()

        self.device_id = packet['did']
        self._timestamp = packet['ts']
        self.conditions = packet['conditions']

    @staticmethod
    def try_create(packet: dict, host: str):
        log.debug("Trying to create UDP conditions packet")
        try:
            return WlUdpBroadcastPacket(packet, host)
        except (ValueError, KeyError) as e:
            raise weewx.WeeWxIOError("Could not extract main entries of packet") from e

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def _conditions(self) -> dict:
        return self.conditions

    @property
    def data_source(self) -> PacketSource:
        return PacketSource.WEATHER_PUSH
