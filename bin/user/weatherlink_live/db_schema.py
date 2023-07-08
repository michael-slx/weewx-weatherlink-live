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

import weewx.units
from schemas import wview_extended

_temperature_fields = ["dewpoint2",
                       "dewpoint3",
                       "dewpoint4",
                       "dewpoint5",
                       "dewpoint6",
                       "dewpoint7",
                       "dewpoint8",
                       "heatindex2",
                       "heatindex3",
                       "heatindex4",
                       "heatindex5",
                       "heatindex6",
                       "heatindex7",
                       "heatindex8",
                       "wetbulb",
                       "wetbulb1",
                       "wetbulb2",
                       "wetbulb3",
                       "wetbulb4",
                       "wetbulb5",
                       "wetbulb6",
                       "wetbulb7",
                       "wetbulb8",
                       "thw",
                       "thsw",
                       "inHeatindex"]
_rain_count_fields = ['rainCount']  # unit: count
_rain_count_rate_fields = ['rainCountRate']  # unit: count per hour
_rain_amount_fields = ['rainSize']  # unit: technically rain amount (inch/mm)

_TABLE_FIELDS = wview_extended.table \
                + [(field, "REAL") for field in _temperature_fields] \
                + [(field, "REAL") for field in _rain_count_fields] \
                + [(field, "REAL") for field in _rain_count_rate_fields] \
                + [(field, "REAL") for field in _rain_amount_fields]

_DAY_SUMMARIES_FIELDS = wview_extended.day_summaries \
                        + [(field, "SCALAR") for field in _temperature_fields] \
                        + [(field, "SCALAR") for field in _rain_count_fields] \
                        + [(field, "SCALAR") for field in _rain_count_rate_fields] \
                        + [(field, "SCALAR") for field in _rain_amount_fields]

db_schema = {'table': _TABLE_FIELDS, 'day_summaries': _DAY_SUMMARIES_FIELDS}


def configure_units() -> None:
    # Define units of new observation
    weewx.units.obs_group_dict.update(dict([(observation, "group_temperature") for observation in _temperature_fields]))
    weewx.units.obs_group_dict.update(dict([(observation, "group_count") for observation in _rain_count_fields]))
    weewx.units.obs_group_dict.update(dict([(observation, "group_rate") for observation in _rain_count_rate_fields]))
    weewx.units.obs_group_dict.update(dict([(observation, "group_rain") for observation in _rain_amount_fields]))

    # Define unit group 'group_rate'
    weewx.units.USUnits['group_rate'] = 'per_hour'
    weewx.units.MetricUnits['group_rate'] = 'per_hour'
    weewx.units.MetricWXUnits['group_rate'] = 'per_hour'

    weewx.units.default_unit_format_dict['per_hour'] = '%.0f'
    weewx.units.default_unit_label_dict['per_hour'] = ' per hour'
