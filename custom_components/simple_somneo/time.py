"""Time entities for Somneo."""
from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SomneoConfigEntry
from .entity import SomneoWakeupEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SomneoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""
    async_add_entities([SomneoWakeupTime(config_entry.runtime_data, "time")])


class SomneoWakeupTime(SomneoWakeupEntity, TimeEntity):
    """Representation of the wake-up alarm time."""

    @property
    def native_value(self) -> time | None:
        """Return the time of the wake-up alarm."""
        return self._value

    async def async_set_value(self, value: time) -> None:
        """Adjust alarm time."""
        await self.coordinator.async_set_wakeup(alarm_time=value)
