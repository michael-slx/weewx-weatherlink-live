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

Users that make use of these advanced features have to ensure that WeeWX can connect to the WeatherLink Live via HTTP (TCP port `80`). Additionally, the WeatherLink Live sends real-time updates by broadcasting on UDP port `22222`.

## Prerequisites

If you haven't done so already, install the following packages:

- **Python 3**: WeeWX itself can run on either Python 2 or 3. This driver however requires Python 3.
- **WeeWX** including all of its dependencies
- **Python module `requests`**: This driver uses the Python `requests` module for communicating with the WeatherLink device.

## Installing the driver

1. Download the newest release of the driver from the [Releases section](https://github.com/michael-slx/weewx-weatherlink-live/releases).

2. On the WeeWX device, install the extension by running the following command, possibly using `sudo`.

Replace the file name with the actual name of the file you downloaded in the previous step.

```sh
# Replace file name
> wee_extension --install=weewx-weatherlink-live.tar.xz
```

3. Reconfigure WeeWX by running the following command, possibly using `sudo`.

```sh
> wee_config --reconfigure
```

4. Answer all promots by providing information about your location, altitude, etc..

5. When asked to choose a driver, select **WeatherLinkLive (`user.weatherlink_live_driver`)**.

**Example:**

```
Installed drivers include:
  0) WeatherLinkLive (user.weatherlink_live_driver)
  1) AcuRite         (weewx.drivers.acurite)
  2) CC3000          (weewx.drivers.cc3000)
  3) FineOffsetUSB   (weewx.drivers.fousb)
  4) Simulator       (weewx.drivers.simulator)
  5) TE923           (weewx.drivers.te923)
  6) Ultimeter       (weewx.drivers.ultimeter)
  7) Vantage         (weewx.drivers.vantage)
  8) WMR100          (weewx.drivers.wmr100)
  9) WMR300          (weewx.drivers.wmr300)
 10) WMR9x8          (weewx.drivers.wmr9x8)
 11) WS1             (weewx.drivers.ws1)
 12) WS23xx          (weewx.drivers.ws23xx)
 13) WS28xx          (weewx.drivers.ws28xx)
choose a driver [4]: 0
```

6. Enter the **IP address or hostname** of your WeatherLink Live.

If you do not know this, you can look it up in the WeatherLink app, on WeatherLink.com or on the configuration interface of your router.

**Example:**

```
IP/Hostname: weatherlinklive.localdomain
```

7. Choose a mapping template.

Unfortunately, there is no way to automatically detect which combination of transmitters and sensors you have connected to your WeatherLink Live. Therefore it is necessary to manually configure the assignment of measurements to WeeWX metrics.

These assignments are combined into logical groups called "mappings". Depending on the type of mapping, each mapping may require additional configuration such as the transmitter id.

To ease initial setup, this driver provides mapping templates for the most common sensor configurations.

Choose one of the templates when the respective prompt appears during the configuration process. Enter no answer if you do not wish to use any template. The prompt only appears if there's no mapping configured.

Additional information on how to manually configure mappings can be found in the dedicated [Configuration documentation](configuration.md).

**Example:**

```
Mapping templates:
  0: Vantage Pro 2
  1: Vantage Pro 2 Plus
Use template (blank for none) []: 1
```

8. If you wish to **inspect the configured mappings**, you can run the following command to display a table of assignments from sensors to WeeWX metrics.

```sh
> wee_device --print-mapping
```

9. Switch to custom database schema.

Your Davis weather station can measure many more things than WeeWX can store by default. If you wish to use the full potential of your WeatherLink Live, it is recommended you switch to the database schema that is provided by this driver.

An explanation of how to switch database schemas can be found in the official WeeWX documentation: [Customizing the database](http://www.weewx.com/docs/customizing.htm#archive_database).<br>
The schema is called ``user.weatherlink_live.schema`

## Further configuration

If you want to further customize your configuration, you can find additional instructions in the [Configuration reference](configuration.md).