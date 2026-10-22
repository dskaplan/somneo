"""Data update coordinator for Somneo."""
from __future__ import annotations

import asyncio
import logging
from datetime import time, timedelta
from time import monotonic
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pysomneo import FM_PRESETS, Somneo

from .const import (
    DOMAIN,
    STATUS_ALARM,
    STATUS_AUDIO,
    STATUS_LIGHT,
    STATUS_OFF,
    STATUS_RELAX_BREATHE,
    STATUS_SNOOZE,
    STATUS_SUNSET,
    STATUS_WAKE_UP,
    WAKEUP_ALARM,
)

_LOGGER = logging.getLogger(__name__)

# Default scan interval (seconds); can be overridden by config entry options
DEFAULT_SCAN_INTERVAL = 10
# The wake-up profile only changes when somebody edits the alarm.
WAKEUP_PROFILE_INTERVAL = 60
# The Somneo regularly drops a request, only report it after a few in a row.
MAX_FAILURES = 3

SOUND_OFF = "off"

type SomneoConfigEntry = ConfigEntry[SomneoCoordinator]


def decode_status(wusts: int) -> str:
    """Decode the status bit field of the Somneo."""
    if wusts & 1 << 11:  # An alarm is running
        if wusts & 1 << 4:
            return STATUS_SNOOZE
        if wusts & 1 << 9:
            return STATUS_ALARM
        return STATUS_WAKE_UP
    if wusts & 1 << 3:
        return STATUS_SUNSET
    if wusts & 1 << 6:
        return STATUS_RELAX_BREATHE
    if wusts & 1 << 9:
        return STATUS_AUDIO
    if wusts & 1 << 8:
        return STATUS_LIGHT
    return STATUS_OFF


class SomneoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Representation of a Somneo Coordinator."""

    config_entry: SomneoConfigEntry

    def __init__(self, hass: HomeAssistant, entry: SomneoConfigEntry) -> None:
        """Initialize Somneo client."""
        self.somneo = Somneo(entry.data[CONF_HOST])
        self.light_themes: list[str] = []
        self.sounds: list[str] = []
        # pysomneo queues requests on a single connection, the lock keeps a
        # command from interleaving with the requests of an update.
        self._lock = asyncio.Lock()
        self._failures = 0
        self._profile: dict[str, Any] = {}
        self._profile_fetched: float | None = None

        # Allow the scan interval to be configurable via config entry options
        scan_seconds = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        try:
            scan_interval = timedelta(seconds=int(scan_seconds))
        except Exception:
            scan_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=scan_interval,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            ),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest data."""
        try:
            async with self._lock:
                data = await self._fetch()
        except Exception as err:
            self._failures += 1
            if self.data is None or self._failures >= MAX_FAILURES:
                raise UpdateFailed(f"Error fetching data from Somneo: {err}") from err
            _LOGGER.debug("Somneo fetch failed, using previous data: %s", err)
            return self.data
        self._failures = 0
        return data

    async def _fetch(self) -> dict[str, Any]:
        """Fetch all data from the Somneo."""
        somneo = self.somneo
        # pysomneo only refreshes the lights, alarms and player once a minute
        # unless forced, the coordinator sets the pace instead.
        data = await somneo.fetch_data(force_slow_refresh=True)

        if not self.light_themes:
            self.light_themes = list(somneo.wake_light_themes)
            self.sounds = [SOUND_OFF, *somneo.wake_sound_themes, *FM_PRESETS]

        if (
            self._profile_fetched is None
            or monotonic() - self._profile_fetched >= WAKEUP_PROFILE_INTERVAL
        ):
            self._profile = await self._fetch_wakeup_profile()
            self._profile_fetched = monotonic()

        alarm = data["alarms"][WAKEUP_ALARM]
        return {
            **data,
            "status": decode_status(int(somneo.alarm_status["wusts"])),
            "wakeup": {
                "enabled": alarm["enabled"],
                "time": alarm["time"],
                "days": alarm["days_type"],
                **self._profile,
            },
        }

    async def _fetch_wakeup_profile(self) -> dict[str, Any]:
        """Fetch the light and sound settings of the wake-up alarm."""
        somneo = self.somneo
        profile = await somneo.get_alarm_details(WAKEUP_ALARM)
        try:
            source = profile["snddv"]
            if source == "off":
                sound = SOUND_OFF
            elif source == "fmr":
                sound = f"fm {profile['sndch']}"
            else:
                sound = next(
                    name
                    for name, channel in somneo.wake_sound_themes.items()
                    if channel == int(profile["sndch"])
                )
            return {
                "duration": int(profile["durat"]),
                "brightness": int(profile["curve"]),
                "theme": next(
                    name
                    for name, ctype in somneo.wake_light_themes.items()
                    if ctype == int(profile["ctype"])
                ),
                "sound": sound,
                "volume": int(profile["sndlv"]),
            }
        except (KeyError, TypeError, ValueError, StopIteration):
            _LOGGER.debug("Unexpected wake-up profile: %s", profile)
            return self._profile

    async def _async_call(self, func: Any, *args: Any, **kwargs: Any) -> None:
        """Send a command to the Somneo and refresh the data."""
        try:
            async with self._lock:
                await func(*args, **kwargs)
        except Exception as err:
            raise HomeAssistantError(f"Somneo command failed: {err}") from err
        await self.async_request_refresh()

    async def async_close(self) -> None:
        """Close the connection to the Somneo."""
        # pysomneo does not expose closing its aiohttp session.
        await self.somneo._client.session.close()  # noqa: SLF001

    async def async_toggle_light(
        self, state: bool, brightness: int | None = None
    ) -> None:
        """Toggle the main light."""
        await self._async_call(self.somneo.toggle_light, state, brightness=brightness)

    async def async_toggle_nightlight(self, state: bool) -> None:
        """Toggle the night light."""
        await self._async_call(self.somneo.toggle_night_light, state)

    async def async_dismiss_alarm(self) -> None:
        """Dismiss alarm."""
        await self._async_call(self.somneo.dismiss_alarm)

    async def async_snooze_alarm(self) -> None:
        """Snooze alarm."""
        await self._async_call(self.somneo.snooze_alarm)

    async def async_set_snooze_time(self, snooze_time: int) -> None:
        """Set snooze time."""
        await self._async_call(self.somneo.set_snooze_time, snooze_time)

    async def async_player_toggle(self, state: bool) -> None:
        """Toggle the audio player."""
        await self._async_call(self.somneo.toggle_player, state)

    async def async_set_player_volume(self, volume: float) -> None:
        """Set the volume of the audio player."""
        await self._async_call(self.somneo.set_player_volume, volume)

    async def async_set_player_source(self, source: str) -> None:
        """Set the source of the audio player."""
        await self._async_call(self.somneo.set_player_source, source)

    async def async_toggle_wakeup(self, state: bool) -> None:
        """Toggle the wake-up alarm."""
        await self._async_call(self.somneo.toggle_alarm, WAKEUP_ALARM, state)

    async def async_set_wakeup(
        self, alarm_time: time | None = None, days: str | None = None
    ) -> None:
        """Set the time and days of the wake-up alarm."""
        await self._async_call(
            self.somneo.set_alarm, WAKEUP_ALARM, v_time=alarm_time, days=days
        )

    async def async_set_wakeup_light(self, **changes: Any) -> None:
        """Adjust the theme, brightness or duration of the wake-up light."""
        profile = self._changed_profile(changes)
        await self._async_call(
            self.somneo.set_alarm_light,
            WAKEUP_ALARM,
            curve=profile["theme"],
            level=profile["brightness"],
            duration=profile["duration"],
        )

    async def async_set_wakeup_sound(self, **changes: Any) -> None:
        """Adjust the sound or volume of the wake-up alarm."""
        profile = self._changed_profile(changes)
        sound = profile["sound"]
        if sound == SOUND_OFF:
            source, channel = "off", ""
        elif sound in FM_PRESETS:
            source, channel = "radio", sound.removeprefix("fm ")
        else:
            source, channel = "wake-up", sound
        await self._async_call(
            self.somneo.set_alarm_sound,
            WAKEUP_ALARM,
            source=source,
            channel=channel,
            level=profile["volume"],
        )

    def _changed_profile(self, changes: dict[str, Any]) -> dict[str, Any]:
        """Return the wake-up profile with the changes applied."""
        if not self._profile:
            raise HomeAssistantError("The wake-up settings are not known yet")
        # Read the profile back from the Somneo at the next update.
        self._profile_fetched = None
        return {**self._profile, **changes}
