# Changelog

## Version 1.0.0

- First stable release

## Version 1.0.1

### Fix incorrect rain mapping

Storing the actual floating-point value of the rain amount for calculation would cause the rain amount to be reported too low due to floating-point precision errors.

Instead, only the count of spoon trips (an integer) is stored.

### Additional rain observations

Additionally, the rain mapping now exposes three more values:
 - spoon trips since last record
 - rain rate in spoon trips per hour
 - size of spoon in inches

The first uses the unit group `group_count`, the second one `group_rate` (see below) and the latter `group_rain`.

### New unit group `group_rate`

A new unit group `group_rate` is defined. Currently it contains only one unit `per_hour`.
`group_rate ` is intended for observations measuring the instantaneous rate of some event. I.e. how often something it would happen in 60 minutes if the event continued to occur at the current rate. This is comparable to "rain rate" except that it is intended for concrete, countable events.

The driver only uses it for the rate of the rain collector spoon tripping.

### Other bugfixes and changes

- Improve error handling in UDP broadcast receiver
- Improve closing of UDP broadcast receiver
- Make rain mapping and wind service `None`-safe
- Convert all caught errors in driver to `InitializationError ` and `WeeWxIOError `. This improves integration with WeeWX's automatic retries.
- Minor refactoring

## Version 1.0.2

- **Fix incorrect rain diff calculation**
  Previous amount needs to be subtracted from the current amount, not
  vice-versa.

## Version 1.0.3

- **Fix broadcast activation failing after some time**
  After an irregular timespan (usually hours to days) broadcast activation would silently fail. This was due to the polling and broadcast activation happening at the same time. The WLL however is unable to cope with multiple simultaneous HTTP requests.
  This was resolved by implementing a centralized scheduler to avoid multiple tasks being executed simultaneously.

- **Switch all driver threads to "daemon mode"**

## Version 1.0.4

- **Fix high CPU usage** ([#2](https://github.com/michael-slx/weewx-weatherlink-live/issues/2))
  Due to not blocking the loop when no packets were available, this driver caused WeeWX to have an absurdly high CPU utilization. This is now resolved by pausing the loop until a packet is received (or an error is caught). As a safety measure, the driver checks for new data every 5 seconds anyway.

## Version 1.0.5

- **Fix interrupts and signals being caught in main loop** ([#4](https://github.com/michael-slx/weewx-weatherlink-live/issues/4))
  Interrupts and signals were caught in main loop, preventing WeeWX from being stopped using `Ctrl + C` or other signals used by the service manager.
- **Fix log messages in the main packet loop not respecting `log_success` configuration option** ([#3](https://github.com/michael-slx/weewx-weatherlink-live/issues/3))
- **Completely rework scheduling logic**
  All scheduling is now centralized. This should prevent any tasks to be executed immediately one after another. Push refreshing is now performed every 20 minutes and is scheduled using a integer factor of polling events

## Version 1.0.6

### General

- **Add data packet watchdog** ([#11](https://github.com/michael-slx/weewx-weatherlink-live/issues/11))

  If no data packet is emitted for a configurable count of iterations, an error will be raised, in turn crashing the engine (and potentially triggering a restart).
  The count of iterations can be configured by adding the `max_no_data_iterations` option in the driver's section (default is 5). An iteration will happen every 5 seconds when no data is received.

  Thanks to user [cube1us](https://github.com/cube1us) debugging this issue.

### HTTP

- **Retry failed HTTP requests**
  If HTTP requests fail, the driver will attempt to send them again up to 3 times. Should none of the attempts succeed, an exception will be raised.

- **Make HTTP requests honor `socket_timeout` option** in configuration ([#11](https://github.com/michael-slx/weewx-weatherlink-live/issues/11))

  Thanks to user [cube1us](https://github.com/cube1us) debugging this issue.

### Configuration

- **Configure accumulators for custom observations defined by driver**
  `rainCount` is accumulated by summation and for `rainSize` the last available value is used.
- **Move example configuration from installer tool to configuration editor**
  Example configuration now includes comments.
- **Remove `polling_interval` from default stanza**
  It isn't a required option as a sensible default is set.

### Logging

- **Change log message to not read like an error**
  Mapping debug message previously read like an error message. This is now improved.
- **Reduce chattiness of driver during normal operation** ([#10](https://github.com/michael-slx/weewx-weatherlink-live/issues/10))
  The driver previously logged `INFO` messages when emitting packets. This was changed to `DEBUG`.
- **Add additional log messages when receiving and decoding broadcast packets**
  When receiving broadcast messages, the size of the packet will be logged and a message will be printed when creating packet objects.

## Version 1.0.7

- **Fix packet emission loop**

  With the changes of the previous release, push (broadcast) packets prevailed to the point where no push packets were emitted anymore.
