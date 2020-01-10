import requests

from user.weatherlink_live.packets import WlHttpBroadcastStartRequestPacket, WlHttpConditionsRequestPacket


def start_broadcast(host: str, duration):
    r = requests.get("http://%s:80/v1/real_time?duration=%d" % (host, duration))
    json = r.json()
    return WlHttpBroadcastStartRequestPacket.try_create(json, host)


def request_current(host: str):
    r = requests.get("http://%s:80/v1/current_conditions" % host)
    json = r.json()
    return WlHttpConditionsRequestPacket.try_create(json, host)
