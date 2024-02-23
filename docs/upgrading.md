# Upgrade guide

Generally, upgrading this driver only requires downloading and installing the new package using `weectl`. Any additional steps required, will be documented below. If the respective *target* version is not listed, no additional steps are necessary.

If you are also upgrading WeeWX itself, consult the WeeWX Upgrade guide and follow the instructions there.

## Contents

- [Contents](#contents)
- [Upgrading to version 1.1.3 (on WeeWX 5)](#upgrading-to-version-113-on-weewx-5)

## Upgrading to version 1.1.3 (on WeeWX 5)

If the `driver` option of the `WeatherLinkLive` section in the configuration file is `user.weatherlink_live_driver`, change it to `user.weatherlink_live`.
No changes are required, if it already is `user.weatherlink_live`.

```ini
[WeatherLinkLive]
    # This section configures the WeatherLink Live driver.

    # Driver module
    #driver = user.weatherlink_live_driver # <-- Old line
    driver = user.weatherlink_live         # <-- New line

    # Host name or IP address of WeatherLink Live
    host = weatherlink_live

    # Mapping of transmitter ids to WeeWX records
    mapping = th:1, rain:1, wind:1, uv:1, solar:1, windchill:1, thw:1, thsw:1:appTemp, th_indoor, baro, battery:1

```

The old value is deprecated and will be removed in version 1.2.

