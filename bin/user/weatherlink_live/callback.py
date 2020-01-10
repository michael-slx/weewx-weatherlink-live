from user.weatherlink_live.packets import DavisConditionsPacket


class PacketCallback(object):
    """Callback for receiving packets or errors"""

    def on_packet_received(self, packet: DavisConditionsPacket):
        raise NotImplementedError("Abstract type")

    def on_packet_receive_error(self, e: BaseException):
        raise NotImplementedError("Abstract type")
