# WeeWX driver for Davis WeatherLink Live

This is a driver allowing the [WeeWX](http://www.weewx.com/) weather software to retrieve data from the [Davis WeatherLink Live](https://www.davisinstruments.com/weatherlinklive/) data logger (WLL). This driver is fully compatible with the WLL's local API, allowing an update frequency of up to 2.5 seconds.

Unlike other drivers, mixing many sensors transmitting on any id is fully supported.. E.g. an ISS transmitting temperature, humidity and rain on id `1` and a sensor transmitter with wind, solar and UV on id `2`.

Unfortunately the WeatherLink Live currently does not provide a local API to access historic data.
An API is available for WeatherLink subscribers. This driver does however not support this interface.

This drives requires **WeeWX 4**, **Python 3** and the Python **`requests` module**.

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Getting started](#getting-started)
- [Detailed instructions](#detailed-instructions)
- [Configuration](#configuration)
	- [Annotated example configuration](#annotated-example-configuration)
	- [Options reference](#options-reference)
		- [`polling_interval`](#pollinginterval)
		- [`max_no_data_iterations`](#maxnodataiterations)
		- [`host`](#host)
		- [`mapping`](#mapping)
	- [Available mappings](#available-mappings)
	- [Mapping examples](#mapping-examples)
		- [Plain Vantage2 Pro Plus](#plain-vantage2-pro-plus)
		- [Vantage2 Pro Plus with additional anemometer transmitter](#vantage2-pro-plus-with-additional-anemometer-transmitter)
		- [Vantage2 Pro Plus with separate transmitter for wind, solar and UV](#vantage2-pro-plus-with-separate-transmitter-for-wind-solar-and-uv)
		- [Vantage2 Pro Plus with soil/leaf station](#vantage2-pro-plus-with-soilleaf-station)
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
    mapping = th:1, th_indoor, baro, rain:1, wind:1, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, battery

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

| Mapping name                                   | Parameters                       | Description                                                  |
| ---------------------------------------------- | -------------------------------- | ------------------------------------------------------------ |
| **`t`** (temperature)                          | Sensor id                        | Maps outside temperature (no humidity)                       |
| **`th`** (temperature, humidity)               | Sensor id                        | Maps outside temperature, humidity, heat index, dew point and wet bulb temperature |
| **`wind`**                                     | Sensor id                        | Maps wind speed and direction to LOOP speed and direction.<br />An additional service then finds the maximum wind speed during the archive interval and assigns this speed and the respective direction to the gust observations. |
| **`rain`**                                     | Sensor id                        | Maps rain amount and rate as well as count of spoon trips, rate of spoon trips and size of spoon.<br />Differential rain amount is calculated from daily rain measurement. |
| **`solar`** (solar radiation)                  | Sensor id                        | Maps solar radiation                                         |
| **`uv`** (UV index)                            | Sensor id                        | Maps UV index                                                |
| **`windchill`** (wind chill)                   | Sensor id                        | Maps wind chill as reported by the respective transmitter.<br />_**Note:** Only available when thermometer and anemometer are connected to the same transmitter._ |
| **`thw`** (THW index)                          | Sensor id, **Option:** `appTemp` | Maps THW (temperature, humidity, wind) index as reported by the respective transmitter.<br />_**Note:** Only available when thermometer, hygrometer and anemometer are connected to the same transmitter.<br />**Option `appTemp`:** When this option is set (see examples), the THW index value is additionally mapped to the `appTemp` field available in the WeeWX default schema. |
| **`thsw`** (THSW index)                        | Sensor id, **Option:** `appTemp` | Maps THSW (temperature, humidity, solar, wind) index as reported by the respective transmitter.<br />_**Note:** Only available when thermometer, hygrometer, pyranometer and anemometer are connected to the same transmitter._<br />**Option `appTemp`:** When this option is set (see examples), the THSW index value is additionally mapped to the `appTemp` field available in the WeeWX default schema. |
| **`soil_temp`** (soil temperature)             | Sensor id, Sensor number         | Maps soil temperature sensors from soil/leaf stations.       |
| **`soil_moist`** (soil moisture)               | Sensor id, Sensor number         | Maps soil moisture sensors from soil/leaf stations.          |
| **`leaf_wet`** (leaf wetness)                  | Sensor id, Sensor number         | Maps leaf wetness sensors from soil/leaf stations.           |
| **`th_indoor`** (indoor temperature, humidity) | _none_                           | Maps indoor temperature, humidity, heat index and dew point as measured by the WLL itself |
| **`baro`** (barometer)                         | _none_                           | Maps station (absolute) and sea-level pressure as measured/calculated by the WLL itself |
| **`battery`**                                  | _none_                           | Maps the battery status indicator flag of all connected transmitters to the fields `batteryStatus1` to `batteryStatus8`. I.e. the value of transmitter 1 is mapped to `batteryStatus1`, transmitter 2 to `batteryStatus2` and so on.<br />**`0`** = Battery OK; **`1`** = Battery low |

### Mapping examples

#### Plain Vantage2 Pro Plus

This example is a valid mapping for a factory-default Vantage2 Pro Plus. All sensors are connected to the main ISS transmitter set to id 1.

```ini
mapping = th:1, th_indoor, baro, rain:1, wind:1, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, battery
```

#### Vantage2 Pro Plus with additional anemometer transmitter

Same as above, except the wind sensor is connected to a separate transmitter with id 2.

Note that there is a configuration option on WeatherLink.com to import the wind measurement into the measurements of the main transmitter. If you enable this, the wind chill, THW and THSW values will still be calculated. Otherwise they should be removed from the mapping.

```ini
mapping = th:1, th_indoor, baro, rain:1, wind:2, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, battery
```

#### Vantage2 Pro Plus with separate transmitter for wind, solar and UV

Same as above, except the solar and UV sensors are also connected to the separate transmitter with id 2. Useful when the shadow cast by a building would otherwise obstruct solar and UV sensors.

Note that THSW will not be calculated anymore since the solar sensor is now on a separate transmitter and unlike the wind measurements there's no configuration option.

```ini
mapping = th:1, th_indoor, baro, rain:1, wind:2, uv:2, solar:2, thw:1:appTemp, windchill:1, battery
```

#### Vantage2 Pro Plus with soil/leaf station

Same as the first example with an additional soil/leaf station. The agriculture station has the transmitter id 2. 4 soil temperature sensors, 4 soil moisture sensors and 2 leaf wetness sensors are connected.

Note that the ordering of the mapping matters: Mappings named earlier are mapped to the "lower-numbered" database columns. Remember this fact if you wish to add additional sensors later on.

```ini
mapping = th:1, th_indoor, baro, rain:1, wind:1, uv:1, solar:1, thw:1, thsw:1:appTemp, windchill:1, soil_temp:2:1, soil_temp:2:2, soil_temp:2:3, soil_temp:2:4, soil_moist:2:1, soil_moist:2:2, soil_moist:2:3, soil_moist:2:4, leaf_wet:2:1, lef_wet:2:2, battery
```

## Contribution

Any contributions to this project are absolutely welcome: issues, documentation and even pull requests. Regarding the latter: Even though there's no official code style, please follow usual Python style conventions.

## Legal

This project is licensed under the MIT license. See the `LICENSE` file for a copy of the license.

While this project uses the WeatherLink Live local API, it is neither supported nor endorsed by Davis Instruments. The same also goes for WeeWX.

All trademarks are held by their respective owners.
