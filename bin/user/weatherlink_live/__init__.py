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
WeeWX driver for WeatherLink Live and AirLink
"""

import user.weatherlink_live.db_schema
from user.weatherlink_live.config_editor import WeatherlinkLiveConfEditor
from user.weatherlink_live.configurator import WeatherlinkLiveConfigurator
from user.weatherlink_live.driver import WeatherlinkLiveDriver
from user.weatherlink_live.static.version import DRIVER_NAME, DRIVER_VERSION

schema = db_schema.db_schema
db_schema.configure_units()


def loader(config_dict, engine):
    return WeatherlinkLiveDriver(config_dict, engine)


def configurator_loader(config_dict):
    return WeatherlinkLiveConfigurator()


def confeditor_loader():
    return WeatherlinkLiveConfEditor()
