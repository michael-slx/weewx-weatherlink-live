# Installation instructions

Welcome to the installation instructions for the WeatherLink Live driver for WeeWX.

## Contents

- [Contents](#contents)
- [Network requirements](#network-requirements)
- [Prerequisites](#prerequisites)
- [Installing the driver](#installing-the-driver)
- [Further configuration](#further-configuration)


## Network requirements

In order for this driver to work properly, the WeatherLink Live has to be on the same VLAN/subnet than the device WeeWX is running on.

If you have simply connected both devices to your home WiFi or router, this is probably the case automatically.

Users of an advanced network setup have to ensure that WeeWX can connect to the WeatherLink Live via HTTP (TCP port `80`). Additionally, the WeatherLink Live sends real-time updates by broadcasting on UDP port `22222`.

## Prerequisites

If you haven't done so already, install the following packages:

- **Python 3.7** or later
- **WeeWX 5** including all of its dependencies
- **Python module `requests`**: This driver uses the Python `requests` module for communicating with the WeatherLink device.

## Installing the driver

1. Install the extension by running the following command, possibly using `sudo`.

```sh
> weectl extension install https://github.com/michael-slx/weewx-weatherlink-live/releases/download/v1.1.4/weewx-weatherlink-live-v1.1.4.tar.xz
```

Answer `y` (Yes), when asked if you want to install the extension.

3. Reconfigure WeeWX by running the following command, possibly using `sudo`.

```sh
> weectl station reconfigure
```

4. Answer all promots by providing information about your location, altitude, etc..

5. When asked to choose a driver, select **WeatherLinkLive (`user.weatherlink_live`)**.

Please ignore the second WeatherLinkLive entry (ending in `_driver`). It is only there for backwards-compatibility with old configuration from WeeWX 4. If you happen to choose this, you will get a warning in your log file.

**Example:**

```
Choose a driver. Installed drivers include:
  0) WeatherLinkLive (user.weatherlink_live)
  1) WeatherLinkLive (user.weatherlink_live_driver)
  2) AcuRite         (weewx.drivers.acurite)
  3) CC3000          (weewx.drivers.cc3000)
  4) FineOffsetUSB   (weewx.drivers.fousb)
  5) Simulator       (weewx.drivers.simulator)
  6) TE923           (weewx.drivers.te923)
  7) Ultimeter       (weewx.drivers.ultimeter)
  8) Vantage         (weewx.drivers.vantage)
  9) WMR100          (weewx.drivers.wmr100)
 10) WMR300          (weewx.drivers.wmr300)
 11) WMR9x8          (weewx.drivers.wmr9x8)
 12) WS1             (weewx.drivers.ws1)
 13) WS23xx          (weewx.drivers.ws23xx)
 14) WS28xx          (weewx.drivers.ws28xx)
driver [5]: 0
```

1. Enter the **IP address or hostname** of your WeatherLink Live.

If you do not know this, you can look it up in the WeatherLink app, on WeatherLink.com or on the configuration interface of your router.

**Example:**

```
IP/Hostname: weatherlinklive
```

7. Choose a mapping template.

Unfortunately, there is no way to automatically detect which combination of transmitters and sensors you have connected to your WeatherLink Live. Therefore it is necessary to manually configure the assignment of measurements to WeeWX metrics.

These assignments are combined into groups called "mappings". Depending on the type of mapping, additional configuration such as the transmitter id may be required.

To ease initial setup, this driver provides mapping templates for the most common sensor configurations.

Choose one of the templates when the respective prompt appears during the configuration process.

The chosen template will overwrite any existing configuration. Enter no answer if you do not wish to use any template.

Additional information on how to manually configure mappings can be found in the dedicated [Configuration documentation](configuration.md).

**Example:**

```
Mapping templates:
  0: Vantage Pro2 or Vantage Vue
  1: Vantage Pro2 Plus
  2: Vantage Pro2 Plus with additional anemometer transmitter
  3: Vantage Pro2 Plus with soil/leaf station
Use template (blank for none) []: 1
```

1. If you wish to **inspect the configured mappings**, you can run the following command to display a table of assignments from sensors to WeeWX metrics.

```sh
> weectl device --print-mapping
```

9. Switch to custom database schema.

Your Davis weather station can measure many more things than WeeWX can store by default. If you wish to use the full potential of your WeatherLink Live, it is recommended you switch to the database schema that is provided by this driver.

An explanation of how to switch database schemas can be found in the official WeeWX documentation: [Customizing the database](http://www.weewx.com/docs/customizing.htm#archive_database).<br>
The schema is called ``user.weatherlink_live.schema`

## Further configuration

If you want to further customize your configuration, you can find additional instructions in the [Configuration reference](configuration.md).
