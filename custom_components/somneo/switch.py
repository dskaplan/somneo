"""Switch entities for Somneo."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SomneoConfigEntry
from .entity import SomneoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SomneoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""
    async_add_entities([SomneoWakeupToggle(config_entry.runtime_data, "wakeup")])


class SomneoWakeupToggle(SomneoEntity, SwitchEntity):
    """Representation of the wake-up alarm switch."""

    _attr_translation_key = "wakeup"

    @property
    def is_on(self) -> bool:
        """Return if the wake-up alarm is enabled."""
        return self.coordinator.data["wakeup"]["enabled"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self.coordinator.async_toggle_wakeup(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self.coordinator.async_toggle_wakeup(False)
