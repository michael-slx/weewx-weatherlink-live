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