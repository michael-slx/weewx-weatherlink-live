# WeeWX driver for Davis WeatherLink Live

This is a driver allowing the [WeeWX](http://www.weewx.com/) weather software to retrieve data from the [Davis WeatherLink Live](https://www.davisinstruments.com/weatherlinklive/) data logger (WLL). This driver is fully compatible with the WLL's local API, allowing an update frequency of up to 2.5 seconds.

Unlike other drivers, mixing many sensors transmitting on any id is fully supported.. E.g. an ISS transmitting temperature, humidity and rain on id `1` and a sensor transmitter with wind, solar and UV on id `2`.

Unfortunately the WeatherLink Live currently does not provide a local API to access historic data.
An API is available for WeatherLink subscribers. This driver does however not support this interface.
You also need to ensure that the WeatherLink Live is on the same LAN subnet as WeeWX, so that UDP broadcasts can be received.

This driver requires **WeeWX 4** or **5**, **Python 3.7** (or later) and the Python **`requests` module**.

## Contents

- [Contents](#contents)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Legal](#legal)


## Documentation

- [**Installation manual**](docs/installation.md)
- [**Configuration reference**](docs/configuration.md)
- [**Troubleshooting**](docs/troubleshooting.md)

## Contribution

Any contributions to this project are absolutely welcome: issues, documentation and even pull requests.

## Legal

This project is licensed under the MIT license. See the `LICENSE` file for a copy of the license.

While this project uses the WeatherLink Live local API, it is neither supported nor endorsed by Davis Instruments. The same also goes for WeeWX.

All trademarks are held by their respective owners.
