'''
WeeWX extension installer
'''

from weecfg.extension import ExtensionInstaller


def loader():
    return WeatherLinkLiveInstaller()


class WeatherLinkLiveInstaller(ExtensionInstaller):
    def __init__(self):
        super(WeatherLinkLiveInstaller, self).__init__(
            name='weatherlink-live',
            version="1.0.0-rc1",
            description='WeeWX driver for Davis WeatherLink Live.',
            author="Michael Schantl",
            author_email="floss@schantl-lx.at",
            config={
                'Station': {
                    'station_type': 'WeatherLinkLive'
                },
                'WeatherLinkLive': {
                    'driver': 'user.weatherlink_live',
                    'host': 'weatherlink',
                    'polling_interval': '10',
                    'mapping': ''
                }
            },
            files=[
                ('bin/user/weatherlink_live', [
                    'bin/user/weatherlink_live/__init__.py',
                    'bin/user/weatherlink_live/callback.py',
                    'bin/user/weatherlink_live/configuration.py',
                    'bin/user/weatherlink_live/data_host.py',
                    'bin/user/weatherlink_live/davis_broadcast.py',
                    'bin/user/weatherlink_live/davis_http.py',
                    'bin/user/weatherlink_live/mappers.py',
                    'bin/user/weatherlink_live/packets.py',
                    'bin/user/weatherlink_live/service.py',
                    'bin/user/weatherlink_live/targets.py',
                    'bin/user/weatherlink_live/utils.py',
                ]),
                ('bin/user/weatherlink_live/static', [
                    'bin/user/weatherlink_live/static/__init__.py',
                    'bin/user/weatherlink_live/static/config.py',
                    'bin/user/weatherlink_live/static/packets.py',
                ]),
            ]
        )
