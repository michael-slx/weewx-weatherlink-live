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
            version="1.2.0",
            description='WeeWX driver for Davis WeatherLink Live.',
            author="Michael Schantl",
            author_email="floss@schantl-lx.at",
            files=[
                ('bin/user', [
                    'bin/user/weatherlink_live_driver.py',
                ]),
                ('bin/user/weatherlink_live', [
                    'bin/user/weatherlink_live/__init__.py',
                    'bin/user/weatherlink_live/callback.py',
                    'bin/user/weatherlink_live/cli.py',
                    'bin/user/weatherlink_live/config_display.py',
                    'bin/user/weatherlink_live/config_editor.py',
                    'bin/user/weatherlink_live/configuration.py',
                    'bin/user/weatherlink_live/configurator.py',
                    'bin/user/weatherlink_live/data_host.py',
                    'bin/user/weatherlink_live/davis_broadcast.py',
                    'bin/user/weatherlink_live/davis_http.py',
                    'bin/user/weatherlink_live/db_schema.py',
                    'bin/user/weatherlink_live/driver.py',
                    'bin/user/weatherlink_live/mappers.py',
                    'bin/user/weatherlink_live/network_test.py',
                    'bin/user/weatherlink_live/packets.py',
                    'bin/user/weatherlink_live/scheduler.py',
                    'bin/user/weatherlink_live/sensor_prompt.py',
                    'bin/user/weatherlink_live/sensors.py',
                    'bin/user/weatherlink_live/service.py',
                    'bin/user/weatherlink_live/utils.py',
                ]),
                ('bin/user/weatherlink_live/static', [
                    'bin/user/weatherlink_live/static/__init__.py',
                    'bin/user/weatherlink_live/static/config.py',
                    'bin/user/weatherlink_live/static/interactive.py',
                    'bin/user/weatherlink_live/static/labels.py',
                    'bin/user/weatherlink_live/static/packets.py',
                    'bin/user/weatherlink_live/static/targets.py',
                    'bin/user/weatherlink_live/static/version.py',
                ]),
            ]
        )
