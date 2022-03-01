# WeeWX driver for Davis WeatherLink Live

This is a driver allowing the [WeeWX](http://www.weewx.com/) weather software to retrieve data from the [Davis WeatherLink Live](https://www.davisinstruments.com/weatherlinklive/) data logger (WLL). This driver is fully compatible with the WLL's local API, allowing an update frequency of up to 2.5 seconds.

Unlike other drivers, mixing many sensors transmitting on any id is fully supported.. E.g. an ISS transmitting temperature, humidity and rain on id `1` and a sensor transmitter with wind, solar and UV on id `2`.

Unfortunately the WeatherLink Live currently does not provide a local API to access historic data.
An API is available for WeatherLink subscribers. This driver does however not support this interface.
You also need to ensure that the WeatherLink Live is on the same LAN subnet as WeeWX, so that UDP broadcasts can be received.

This driver requires **WeeWX 4**, **Python 3** and the Python **`requests` module**.

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Getting started](#getting-started)
- [Detailed instructions](#detailed-instructions) 
	- [Ensuring UDP broadcasts are received](#ensuring-udp-broadcasts-are-received)
- [Configuration](#configuration)
	- [Annotated example configuration](#annotated-example-configuration)
	- [Options reference](#options-reference)
		- [`polling_interval`](#polling_interval)
		- [`max_no_data_iterations`](#max_no_data_iterations)
		- [`host`](#host)
		- [`mapping`](#mapping)
	- [Available mappings](#available-mappings)
	- [Mapping examples](#mapping-examples)
		- [Plain Vantage2 Pro Plus](#plain-vantage2-pro-plus)
		- [Vantage2 Pro Plus with additional anemometer transmitter](#vantage2-pro-plus-with-additional-anemometer-transmitter)
		- [Vantage2 Pro Plus with separate transmitter for wind, solar and UV](#vantage2-pro-plus-with-separate-transmitter-for-wind-solar-and-uv)
		- [Vantage2 Pro Plus with soil/leaf station](#vantage2-pro-plus-with-soilleaf-station)
		- [Vantage Vue](#vantage-vue)
	- [Debugging mapping configuration](#debugging-mapping-configuration)
		- [HTTP data](#http-data)
		- [UDP broadcast data](#udp-broadcast-data)
- [Contribution](#contribution)
- [Legal](#legal)

<!-- /TOC -->

## Getting started

_Working WeeWX 4 installation using Python 3 is assumed. As well as that the Python `requests` module is required._

1. **Download release package** or clone repository with Git

2. **Install extension** using `wee_extension` utility:

   ```bash
   $ wee_extension --install=weewx-weatherlink-live.tar.xz
   ```

3. **Switch driver** and **create example config**

   ```bash
   $ wee_config --reconfigure --driver=user.weatherlink_live --no-prompt
   ```

4. **Set `host` and `mapping`** options

5. _Optional:_ Switch to WLL **database schema (`user.weatherlink_live.schema`)**

6. **Restart WeeWX**

## Detailed instructions

Firstly, download the latest release package and install it using the `wee_extension` utility. Remember to specify the correct file name and execute all commands with sufficient permissions (i.e. `sudo`).

```bash
$ wee_extension --install=weewx-weatherlink-live.tar.xz
```

 Then configure WeeWX to use this driver and create the example configuration.

```bash
$ wee_config --reconfigure --driver=user.weatherlink_live --no-prompt
```

Finally, set the required options `host` and `mapping`.

If you wish to store all data measured by your Davis weather station, you may need to switch to the database schema provided by this extension (`user.weatherlink_live.schema`). See the [official WeeWX customization guide](http://www.weewx.com/docs/customizing.htm#archive_database) for additional information. The additional types included in the schema are:

- Extra dewpoint, heat index and wet bulb fields
- THW and THSW index ("feels like temperature")
- Indoor heat index
- Count of rain spoon trips since last packet
- Rate of rain spoon trips
- Configured size of rain spoon

The units of all additionally defined observations are converted as specified in your configuration and skin. In addition to those specified by WeeWX, the driver defines the unit group `group_rate` currently only consisting of one unit: `per_hour`.

### Ensuring UDP broadcasts are received

WeeWX needs to run on the same subnet as your Weatherlink Live.
This is required so that the driver can receive [UDP broadcast updates](https://weatherlink.github.io/weatherlink-live-local-api).
When this has been enabled (automatically by the driver), the Weatherlink Live will start sending UDP broadcast packets every 2.5s to the broadcast address of its current subnet (for example `192.168.1.*`).
If WeeWX is not on that same subnet, or if UDP broadcasts are being blocked by your router, then the driver will not create WeeWX reports and there will be warnings like `Received no data for X iterations` in the WeeWX log.

This should only be a problem if you are running WeeWX in a separate network from the WeatherLink Live itself, such as on a different router or behind a Docker container. Docker containers can fix this via `--network=host`, while Kubernetes containers can use `hostNetwork: true`.

To confirm whether UDP broadcast packets are being received, you can e.g. run `netcat` from the WeeWX machine or container, see [below](#udp-broadcast-data) for an example.

## Configuration

### Annotated example configuration

```ini
[Station]

    # Set to type of station hardware. There must be a corresponding stanza
    # in this file with a 'driver' parameter indicating the driver to be used.
    station_type = WeatherLinkLive

# Section for configuring the WeatherLink Live driver
[WeatherLinkLive]

    # use WLL driver
    driver = user.weatherlink_live

    # Host name or IP address of WeatherLink or AirLinks
    # Do not specify protocol or port
    host = weatherlink

    # Mapping of transmitter ids
    mapping = th:1, th_indoor, baro, rain:1, wind:1, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, battery:1:outTemp:rain:wind:uv

[DataBindings]

    [[wx_binding]]
        database = archive_sqlite
        table_name = archive
        manager = weewx.manager.DaySummaryManager
        # use WLL schema
        schema = user.weatherlink_live.schema

# Configure accumulation for custom observations
[Accumulator]

    [[rainCount]]
        extractor = sum

    [[rainSize]]
        extractor = last

```

### Options reference

#### `polling_interval`

**Minimum:** 10 seconds<br />
**Default:** 10 seconds

The interval in seconds or fractions thereof to wait between polling the WLL.

#### `max_no_data_iterations`

**Minimum:** 1
**Default:** 5

Count of iterations without any data to tolerate before raising an error.

#### `host`

**Default:** _none_<br />
**Required**

Host name or IP address of the WLL. Do not specify an URL or a port; just the host name is enough.

#### `mapping`

**Default:** _empty list_

List of sensors and their ids to import into WeeWX. Each mapping definition consists of the name, the sensor id and the sensor number separated by a colon `:`. Some mappings also support additional options.

```
[Name](:[SensorId](:[SensorNumber]))(:[Options...])
```

### Available mappings

| Mapping name                                   | Parameters                                                   | Description                                                  |
| ---------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **`t`** (temperature)                          | Sensor id                                                    | Maps outside temperature (no humidity)                       |
| **`th`** (temperature, humidity)               | Sensor id                                                    | Maps outside temperature, humidity, heat index, dew point and wet bulb temperature |
| **`wind`**                                     | Sensor id                                                    | Maps wind speed and direction to LOOP speed and direction.<br />An additional service then finds the maximum wind speed during the archive interval and assigns this speed and the respective direction to the gust observations. |
| **`rain`**                                     | Sensor id                                                    | Maps rain amount and rate as well as count of spoon trips, rate of spoon trips and size of spoon.<br />Differential rain amount is calculated from daily rain measurement. |
| **`solar`** (solar radiation)                  | Sensor id                                                    | Maps solar radiation                                         |
| **`uv`** (UV index)                            | Sensor id                                                    | Maps UV index                                                |
| **`windchill`** (wind chill)                   | Sensor id                                                    | Maps wind chill as reported by the respective transmitter.<br />_**Note:** Only available when thermometer and anemometer are connected to the same transmitter._ |
| **`thw`** (THW index)                          | Sensor id,<br/>**Option:** `appTemp`                         | Maps THW (temperature, humidity, wind) index as reported by the respective transmitter.<br />_**Note:** Only available when thermometer, hygrometer and anemometer are connected to the same transmitter.<br />**Option `appTemp`:** When this option is set (see examples), the THW index value is additionally mapped to the `appTemp` field available in the WeeWX default schema. |
| **`thsw`** (THSW index)                        | Sensor id,<br/>**Option:** `appTemp`                         | Maps THSW (temperature, humidity, solar, wind) index as reported by the respective transmitter.<br />_**Note:** Only available when thermometer, hygrometer, pyranometer and anemometer are connected to the same transmitter._<br />**Option `appTemp`:** When this option is set (see examples), the THSW index value is additionally mapped to the `appTemp` field available in the WeeWX default schema. |
| **`soil_temp`** (soil temperature)             | Sensor id, Sensor number                                     | Maps soil temperature sensors from soil/leaf stations.       |
| **`soil_moist`** (soil moisture)               | Sensor id, Sensor number                                     | Maps soil moisture sensors from soil/leaf stations.          |
| **`leaf_wet`** (leaf wetness)                  | Sensor id, Sensor number                                     | Maps leaf wetness sensors from soil/leaf stations.           |
| **`th_indoor`** (indoor temperature, humidity) | _none_                                                       | Maps indoor temperature, humidity, heat index and dew point as measured by the WLL itself |
| **`baro`** (barometer)                         | _none_                                                       | Maps station (absolute) and sea-level pressure as measured/calculated by the WLL itself |
| **`battery`**                                  | Sensor id, <br/>**Options:** `outTemp`, `rain`, `tx`, `uv`, `wind` | Maps the battery status indicator flag the specified transmitter to the fields `batteryStatus1` to `batteryStatus8`.<br />**Options:** One or more options can be specified to map the battery status of the respective transmitter to the named battery field.<br />_`outTemp`_ = `outTempBatteryStatus`; _`rain`_ = `rainBatteryStatus`; _`tx`_ = `txBatteryStatus`; _`uv`_ = `uvBatteryStatus`; _`wind`_ = `windBatteryStatus`<br />**`0`** = Battery OK; **`1`** = Battery low |

### Mapping examples

#### Plain Vantage2 Pro Plus

This example is a valid mapping for a factory-default Vantage2 Pro Plus. All sensors are connected to the main ISS transmitter set to id 1.

> mapping = th:1, th_indoor, baro, rain:1, wind:1, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, battery:1:outTemp:rain:wind:uv

#### Vantage2 Pro Plus with additional anemometer transmitter

Same as above, except the wind sensor is connected to a separate transmitter with id 2.

Note that there is a configuration option on WeatherLink.com to import the wind measurement into the measurements of the main transmitter. If you enable this, the wind chill, THW and THSW values will still be calculated. Otherwise they should be removed from the mapping.

> mapping = th:1, th_indoor, baro, rain:1, wind:2, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, battery:1:outTemp:rain:uv, battery:2:wind

#### Vantage2 Pro Plus with separate transmitter for wind, solar and UV

Same as above, except the solar and UV sensors are also connected to the separate transmitter with id 2. Useful when the shadow cast by a building would otherwise obstruct solar and UV sensors.

Note that THSW will not be calculated anymore since the solar sensor is now on a separate transmitter and unlike the wind measurements there's no configuration option.

> mapping = th:1, th_indoor, baro, rain:1, wind:2, uv:2, solar:2, thw:1:appTemp, windchill:1, battery:1:outTemp:rain, battery:2:wind:uv

#### Vantage2 Pro Plus with soil/leaf station

Same as the first example with an additional soil/leaf station. The agriculture station has the transmitter id 2. 4 soil temperature sensors, 4 soil moisture sensors and 2 leaf wetness sensors are connected.

Note that the ordering of the mapping matters: Mappings named earlier are mapped to the "lower-numbered" database columns. Remember this fact if you wish to add additional sensors later on.

> mapping = th:1, th_indoor, baro, rain:1, wind:1, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, soil_temp:2:1, soil_temp:2:2, soil_temp:2:3, soil_temp:2:4, soil_moist:2:1, soil_moist:2:2, soil_moist:2:3, soil_moist:2:4, leaf_wet:2:1, leaf_wet:2:2, battery:1:outTemp:wind, battery:2:tx

#### Vantage Vue

The Vantage Vue is similar to a Pro except that it doesn't have solar/uv sensors. So from the above examples we can omit `uv`, `solar`, and `thsw` which depend on those sensors being present, then apply the `appTemp` flag to `thw` instead:

> mapping = th:1, th_indoor, baro, rain:1, wind:1, thw:1:appTemp, windchill:1, battery:1:outTemp:rain:tx:wind

### Debugging mapping configuration

You can check your mappings by accessing the WeatherLink Live data directly. This driver consumes both HTTP and broadcast UDP data, so you can check both sources:

#### HTTP data

HTTP data can be checked by accessing `http://[your.weatherlink.live.ip]/v1/current_conditions` and checking which values from the above list are present and which are `null`. The provided `txid` value (typically `1`) is the sensor number that you should use in your mappings. For example:

```bash
$ curl -v http://[my.weatherlink.live.ip]/v1/current_conditions | jq
{
  "data": {
    "did": "[xxxxxxxxxxxx]",
    "ts": 1646165700,
    "conditions": [
      {
        "lsid": 488584,
        "data_structure_type": 1,
        "txid": 1,
        "temp": 56.4,
        "hum": 93,
        "dew_point": 54.4,
        "wet_bulb": 55.2,
        "heat_index": 56.7,
        "wind_chill": 56.4,
        "thw_index": 56.7,
        "thsw_index": null,
        [...]
      },
      {
        "lsid": 488580,
        "data_structure_type": 4,
        "temp_in": 66.9,
        "hum_in": 46.6,
        "dew_point_in": 45.8,
        "heat_index_in": 65.2
      },
      {
        "lsid": 488579,
        "data_structure_type": 3,
        "bar_sea_level": 30.36,
        "bar_trend": 0.062,
        "bar_absolute": 30.253
      }
    ]
  },
  "error": null
}
```

In this example we see several values under `txid: 1` (so, sensor id `1`) for the weather station, followed by indoor data (at the WeatherLink Live), followed by barometric data at the weather station. In this case we are looking at a Vantage Vue, where `thw` is provided while `thsw` is `null`. `null` indicates that a sensor is not present and so we can exclude that item our mapping configuration.

#### UDP broadcast data

Some data is sent as a UDP broadcast packet every 2.5s. We can sample data by running `netcat` on a machine that's on the same LAN subnet as the WeatherLink Live (note that WeeWX should also be run on this subnet):

```bash
$ nc -nvulp 22222
Bound on 0.0.0.0 22222
Connection received on [my.weatherlink.live.ip] 11851
{"did":"[xxxxxxxxxxxx]","ts":1646168724,"conditions":[{"lsid":488584,"data_structure_type":1,"txid":1,"wind_speed_last":1.43,"wind_dir_last":183,"rain_size":1,"rain_rate_last":0,"rain_15_min":0,"rain_60_min":2,"rain_24_hr":4,"rain_storm":4,"rain_storm_start_at":1646162220,"rainfall_daily":4,"rainfall_monthly":4,"rainfall_year":1039,"wind_speed_hi_last_10_min":5.00,"wind_dir_at_hi_speed_last_10_min":247}]}
```

This shows a subset of the data we received above, but again shows `txid: 1` along with some wind/rain status. This information is also consumed by the mappings.

If you don't see anything for several, you should first check that you are on the same subnet as the WeatherLink Live, and that UDP broadcasts are not blocked in your router settings. If WeeWX hasn't been running for the last ~20 minutes, UDP broadcasts may have automatically turned off, in which case you can reenable them again by accessing `http://[your.weatherlink.live.ip]/v1/real_time?duration=1200` (where `1200` is 20 minutes in seconds).

## Contribution

Any contributions to this project are absolutely welcome: issues, documentation and even pull requests. Regarding the latter: Even though there's no official code style, please follow usual Python style conventions.

## Legal

This project is licensed under the MIT license. See the `LICENSE` file for a copy of the license.

While this project uses the WeatherLink Live local API, it is neither supported nor endorsed by Davis Instruments. The same also goes for WeeWX.

All trademarks are held by their respective owners.
