# Troubleshooting tips

## Contents

- [Contents](#contents)
- [Printing mappings](#printing-mappings)
- [Manually inspecting data](#manually-inspecting-data)
  - [HTTP data](#http-data)
  - [UDP broadcast data](#udp-broadcast-data)


## Printing mappings

If you are unsure which sensor value will be stored in which metric, you can display the mapping table by running the following command:

```sh
> wee_device --print-mapping
```

## Manually inspecting data

If you are unsure which mappings to use or whatever the network connection works property, you can access the WeatherLink Live data directly. This driver consumes both HTTP and broadcast UDP data, so you can check both sources:

### HTTP data

HTTP data can be checked by accessing `http://[your.weatherlink.live.ip]/v1/current_conditions` and checking which values from the above list are present and which are `null`. The provided `txid` value (typically `1`) is the sensor number that you should use in your mappings. For example:

```sh
> curl -v http://[my.weatherlink.live.ip]/v1/current_conditions | jq
```
```json
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
        /*[...]*/
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

### UDP broadcast data

Some data is sent as a UDP broadcast packet every 2.5s. We can sample data by running `netcat` on a machine that's on the same LAN subnet as the WeatherLink Live (note that WeeWX should also be run on this subnet):

```bash
$ nc -nvulp 22222
Bound on 0.0.0.0 22222
Connection received on [my.weatherlink.live.ip] 11851
{"did":"[xxxxxxxxxxxx]","ts":1646168724,"conditions":[{"lsid":488584,"data_structure_type":1,"txid":1,"wind_speed_last":1.43,"wind_dir_last":183,"rain_size":1,"rain_rate_last":0,"rain_15_min":0,"rain_60_min":2,"rain_24_hr":4,"rain_storm":4,"rain_storm_start_at":1646162220,"rainfall_daily":4,"rainfall_monthly":4,"rainfall_year":1039,"wind_speed_hi_last_10_min":5.00,"wind_dir_at_hi_speed_last_10_min":247}]}
```

This shows a subset of the data we received above, but again shows `txid: 1` along with some wind/rain status. This information is also consumed by the mappings.

If you don't see anything for several seconds, you should first check that you are on the same subnet as the WeatherLink Live, and that UDP broadcasts are not blocked in your router settings. If WeeWX hasn't been running for the last ~20 minutes, UDP broadcasts may have automatically turned off, in which case you can reenable them again by accessing `http://[your.weatherlink.live.ip]/v1/real_time?duration=1200` (where `1200` is 20 minutes in seconds).
