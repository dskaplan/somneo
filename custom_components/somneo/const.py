"""Constants for the Somneo integration."""
from typing import Final

DOMAIN: Final = "somneo"

DEFAULT_NAME: Final = "Somneo"

CONF_SESSION: Final = "session"

# The wake-up controls are backed by the first alarm slot of the Somneo
# (shown as the first alarm in the SleepMapper app).
WAKEUP_ALARM: Final = 0

WORKDAYS: Final = "workdays"
WEEKEND: Final = "weekend"
TOMORROW: Final = "tomorrow"
EVERYDAY: Final = "daily"

STATUS_OFF: Final = "off"
STATUS_LIGHT: Final = "light"
STATUS_AUDIO: Final = "audio"
STATUS_SUNSET: Final = "sunset"
STATUS_RELAX_BREATHE: Final = "relax_breathe"
STATUS_WAKE_UP: Final = "wake_up"
STATUS_ALARM: Final = "alarm"
STATUS_SNOOZE: Final = "snooze"

STATUSES: Final = [
    STATUS_OFF,
    STATUS_LIGHT,
    STATUS_AUDIO,
    STATUS_SUNSET,
    STATUS_RELAX_BREATHE,
    STATUS_WAKE_UP,
    STATUS_ALARM,
    STATUS_SNOOZE,
]

# Unique id suffixes of all entities of this integration. Used once, when
# migrating a config entry to version 5, to remove entities of older versions.
ENTITY_KEYS: Final = frozenset(
    {
        "light",
        "nightlight",
        "player",
        "alarm_dismiss",
        "alarm_snooze",
        "temperature",
        "humidity",
        "luminance",
        "noise",
        "next",
        "alarm_status",
        "snooze",
        "wakeup",
        "wakeup_time",
        "wakeup_days",
        "wakeup_theme",
        "wakeup_sound",
        "wakeup_duration",
        "wakeup_brightness",
        "wakeup_volume",
    }
)
