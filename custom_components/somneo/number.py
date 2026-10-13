"""Number entities for Somneo."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SomneoConfigEntry
from .entity import SomneoEntity, SomneoWakeupEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SomneoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        [
            SomneoSnooze(coordinator, "snooze"),
            SomneoWakeupDuration(coordinator, "duration"),
            SomneoWakeupBrightness(coordinator, "brightness"),
            SomneoWakeupVolume(coordinator, "volume"),
        ]
    )


class SomneoSnooze(SomneoEntity, NumberEntity):
    """Representation of a snooze time."""

    _attr_translation_key = "snooze_time"
    _attr_native_min_value = 1
    _attr_native_max_value = 20
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    @property
    def native_value(self) -> int:
        """Return the snooze time."""
        return self.coordinator.data["snooze_time"]

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust snooze time in the UI."""
        await self.coordinator.async_set_snooze_time(int(value))


class SomneoWakeupNumber(SomneoWakeupEntity, NumberEntity):
    """Base class for a numeric setting of the wake-up alarm."""

    _attr_native_step = 1

    @property
    def native_value(self) -> int | None:
        """Return the value of the setting."""
        return self._value


class SomneoWakeupDuration(SomneoWakeupNumber):
    """How long the light takes to reach full brightness before the alarm."""

    _attr_native_min_value = 5
    _attr_native_max_value = 40
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust the duration in the UI."""
        await self.coordinator.async_set_wakeup_light(duration=int(value))


class SomneoWakeupBrightness(SomneoWakeupNumber):
    """The light level reached at the end of the wake-up."""

    _attr_native_min_value = 1
    _attr_native_max_value = 25

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust the brightness in the UI."""
        await self.coordinator.async_set_wakeup_light(brightness=int(value))


class SomneoWakeupVolume(SomneoWakeupNumber):
    """The volume of the wake-up sound."""

    _attr_native_min_value = 1
    _attr_native_max_value = 25

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust the volume in the UI."""
        await self.coordinator.async_set_wakeup_sound(volume=int(value))
