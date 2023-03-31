# Configuration Reference

This document is a reference for all available configuration options.

## Contents

- [Contents](#contents)
- [Example configuration](#example-configuration)
- [Available options](#available-options)
  - [`host`](#host)
  - [`mapping`](#mapping)
  - [`polling_interval`](#polling_interval)
  - [`max_no_data_iterations`](#max_no_data_iterations)
- [Defining mappings](#defining-mappings)
  - [Why are mappings necessary?](#why-are-mappings-necessary)
  - [How are mappings defined?](#how-are-mappings-defined)
  - [Mappings reference](#mappings-reference)
    - [Temperature](#temperature)
    - [Temperature/Humidity](#temperaturehumidity)
    - [Wind](#wind)
    - [Rain](#rain)
    - [Solar irradiation](#solar-irradiation)
    - [UV index](#uv-index)
    - [Wind chill](#wind-chill)
    - [THW index](#thw-index)
    - [THSW index](#thsw-index)
    - [Agricultural temperature](#agricultural-temperature)
    - [Agricultural moisture](#agricultural-moisture)
    - [Leaf wetness](#leaf-wetness)
    - [Battery status](#battery-status)
    - [Indoor temperature/humidity](#indoor-temperaturehumidity)
    - [Barometer](#barometer)
  - [Displaying configured mappings](#displaying-configured-mappings)
  - [Example mappings](#example-mappings)
    - [Vantage Pro2 or Vantage Vue](#vantage-pro2-or-vantage-vue)
    - [Vantage Pro2 Plus](#vantage-pro2-plus)
    - [Vantage Pro2 Plus with additional anemometer transmitter](#vantage-pro2-plus-with-additional-anemometer-transmitter)
    - [Vantage Pro2 Plus with soil/leaf station](#vantage-pro2-plus-with-soilleaf-station)


## Example configuration

```ini
[WeatherLinkLive]
    # Driver module
    driver = user.weatherlink_live_driver

    # Host name or IP address of WeatherLink Live
    host = weatherlinklive.localdomain

    # Mapping of transmitter ids to WeeWX records
    mapping = th:1, rain:1, wind:1, windchill:1, solar:1, uv:1, thw:1, thsw:1:appTemp, th_indoor, baro, battery:1:outTemp:rain:wind

    # Whether to log successful operations.  Overrides top-level setting.
    #log_success = False

    # Whether to log unsuccessful operations. Overrides top-level setting.
    #log_failure = True
```

## Available options

### `host`

**Required:** Yes<br>
**Type:** String

Specifies the hostname or IP address of the WeatherLink Live.

Do not specify an URL or a port; just the host name is enough.

### `mapping`

**Required:** Yes<br>
**Type:** List of Strings<br>
**Minimum:** At least 1 element

Defines all used mappings and their configuration.

List items are separated by a colon character. For readability reasons, whitespace can also be added in between elements.

For more information on defining mappings, see the [Mapping reference](#defining-mappings).

### `polling_interval`

**Required:** No<br>
**Type:** Integer<br>
**Default:** `10` seconds<br>
**Minimum:** `10` seconds

The interval in seconds to wait between retrieving a full data update from the WeatherLink Live.

### `max_no_data_iterations`

**Required:** No<br>
**Type:** Integer<br>
**Default:** `5`<br>
**Minimum:** `1`

Count of iterations without any data to tolerate before raising an error.

The driver checks for the availability of new data at least every 5 secons. If no data is available for the specified number of iterations, an error is raised.

## Defining mappings

The following chapter explains the concept of mappings detailed and in-depth.

### Why are mappings necessary?

Mappings are required because the WeatherLink Live is extremely flexible with regards to the possible combinations of transmitters and sensors. WeeWX however uses a strictly defined database schema to store the recorded data. Unfortunately, there is no way to automatically detect the sensors connected to a WeatherLink Live.

Therefore, sensors have to be manually selected. This is the purpose of mappings.

### How are mappings defined?

Mappings are specified in the `mapping` configuration option. Multiple mapping definitions are separated by a comma (`,`).

**Be careful when changing the order of the mappings! This case cause the data to be mixed up.**<br>
Note that the order in which the mappings are defined does matter. The assignment of sensors to database columns happens in the defined order.
**It is recommended to only ever add mappings to the end.**

Each mapping definition starts with the mapping type. Most mappings require additional options to function property, such as the corresponding transmitter id for the sensor. These additional options are specified after the mapping type and are separated by colons (`:`).

Usually the mapping type correspond to the sensor type. There are however some exceptions: compound metrics such as wind chill. These are calculated by the transmitter internally, which is only possible if all sensors that are required for the calculation are connected to that transmitter.<br>
E.g. to calculate wind chill both the wind sensor and the thermometer have to be connected to the same transmitter.

**Example:**

```ini
mapping = th_indoor, baro, th:1, rain:1, wind:1
```

The above example defines 5 mappings:

1. **Indoor temperature and humidity**: No options necessary because it's an internal sensor.
2. **Barometer**: No options necessary because it's an internal sensor.
3. **Thermometer/hygrometer**: Option `1` means transmitter id `1`.
3. **Rain sensor**: Option `1` means transmitter id `1`.
3. **Wind sensor**: Option `1` means transmitter id `1`.

### Mappings reference

#### Temperature

**Mapping type**: `t`<br>
**Required options**: Transmitter id

**Temperature sensor without a hygrometer**

Maps only the temperature value

#### Temperature/Humidity

**Mapping type**: `th`<br>
**Required options**: Transmitter id

**Temperature sensor with a hygrometer**

Maps temperature, humidity, dew point, heat index and wet bulb.


#### Wind

**Mapping type**: `wind`<br>
**Required options**: Transmitter id

**Wind sensor**

Maps current wind speed and direction as well as gust peak speed and direction.

#### Rain

**Mapping type**: `rain`<br>
**Required options**: Transmitter id

**Rain sensor**

Rain mapping is more complicated because WeeWX stores the differential rain amount (rain between packets). The driver calculates this from the daily rain sum. Additionally, the "raw" values (number of times the rain spoon tripped).

All in all, the following values are mapped:

- Differential rain amount
- Rain rate
- Size of rain measurement spoon
- Differential number of times the rain spoon tripped
- Rate of rain spoon trippings

#### Solar irradiation

**Mapping type**: `solar`<br>
**Required options**: Transmitter id

**Solar irradiation sensor**

Maps solar irradiation value.

#### UV index

**Mapping type**: `uv`<br>
**Required options**: Transmitter id

**UV sensor**

Maps UV index value.

#### Wind chill

**Mapping type**: `windchill`<br>
**Required options**: Transmitter id<br>
**Optional options**: `appTemp`

**Wind chill compound metric**

Maps wind chill temperature value.

Requires both temperature and wind sensor to be connected to the same transmitter.

The optional `appTemp` option also maps the wind chill to the appearant temperature metric.

#### THW index

**Mapping type**: `thw`<br>
**Required options**: Transmitter id<br>
**Optional options**: `appTemp`

**THW index compound metric**

Maps THW (temperature, humidity, wind) index temperature value.

Requires temperature, humidity and wind sensor to be connected to the same transmitter.

The optional `appTemp` option also maps the wind chill to the appearant temperature metric.

#### THSW index

**Mapping type**: `thsw`<br>
**Required options**: Transmitter id<br>
**Optional options**: `appTemp`

**THSW index compound metric**

Maps THSW (temperature, humidity, solar, wind) index temperature value.

Requires temperature, humidity, solar irradiation and wind sensor to be connected to the same transmitter.

The optional `appTemp` option also maps the wind chill to the appearant temperature metric.

#### Agricultural temperature

**Mapping type**: `soil_temp`<br>
**Required options**: Transmitter id, Sensor number

**Soil temperature sensor**

Maps soil temperature value.

The second option specifies the port to which the sensor is connected (1 - 4).

#### Agricultural moisture

**Mapping type**: `soil_moist`<br>
**Required options**: Transmitter id, Sensor number

**Soil moisture sensor**

Maps soil moisture value.

The second option specifies the port to which the sensor is connected (1 - 4).

#### Leaf wetness

**Mapping type**: `leaf_wet`<br>
**Required options**: Transmitter id, Sensor number

**Leaf wetness sensor**

Maps leaf wetness value.

The second option specifies the port to which the sensor is connected (1 or 2).

#### Battery status

**Mapping type**: `battery`<br>
**Required options**: Transmitter id<br>
**Optional options**: Additional mapping targets (`outTemp`, `rain`, `tx`, `uv`, `wind`)

**Status of the transmitter backup battery**

Maps battery status value (`0` or `1`).

Optionally, further mapping options can be specified. These will lead to the status being mapped to additional metrics provided by WeeWX. This is useful for displaying the battery status in the default WeeWX skin.

#### Indoor temperature/humidity

**Mapping type**: `th_indoor`<br>
**Required options**: None

**Internal temperature/humidity sensor of WeatherLink Live**

Maps temperature, humidity, dew point and heat index.

#### Barometer

**Mapping type**: `baro`<br>
**Required options**: None

**Internal barometric sensor of WeatherLink Live**

Maps sea-level and absolute barometric pressure.

### Displaying configured mappings

If you wish to **inspect the configured mappings**, you can run the following command to display a table of assignments from sensors to WeeWX metrics.

```sh
> wee_device --print-mapping
```

### Example mappings

_Note:_ These examples correspond to the templates provided by the interactive setup assistant.

#### Vantage Pro2 or Vantage Vue

This example is a valid mapping for a factory-default Vantage2 Pro. All sensors are connected to the main ISS transmitter set to id 1.

```ini
mapping = th:1, rain:1, wind:1, windchill:1, thw:1:appTemp, battery:1:outTemp:rain:wind, th_indoor, baro
```

#### Vantage Pro2 Plus

This example is a valid mapping for a factory-default Vantage2 Pro Plus. All sensors are connected to the main ISS transmitter set to id 1.

```ini
mapping = th:1, rain:1, wind:1, uv:1, solar:1, windchill:1, thw:1, thsw:1:appTemp, th_indoor, baro, battery:1:outTemp:rain:wind:uv
```

#### Vantage Pro2 Plus with additional anemometer transmitter

Same as above, except the wind sensor is connected to a separate transmitter with id 2.

Note that there is a configuration option on WeatherLink.com to import the wind measurement into the measurements of the main transmitter. If you enable this, the wind chill, THW and THSW values will still be calculated. Otherwise they should be removed from the mapping.

```ini
mapping = th:1, rain:1, wind:2, uv:1, solar:1, windchill:1, thw:1, thsw:1:appTemp, th_indoor, baro, battery:1:outTemp:rain:uv, battery:2:wind
```

#### Vantage Pro2 Plus with soil/leaf station

Same as the second example with an additional (fully equipped) soil/leaf station. The agriculture station has the transmitter id 2.

```ini
mapping = th:1, rain:1, wind:1, uv:1, solar:1, windchill:1, thw:1, thsw:1:appTemp, soil_temp:2:1, soil_temp:2:2, soil_temp:2:3, soil_temp:2:4, soil_moist:2:1, soil_moist:2:2, soil_moist:2:3, soil_moist:2:4, leaf_wet:2:1, leaf_wet:2:2, th_indoor, baro, battery:1:outTemp:wind:uv, battery:2:tx
```
