"""Button entities for Somneo."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    coordinator = config_entry.runtime_data

    async_add_entities(
        [
            SomneoDismiss(coordinator, "alarm_dismiss"),
            SomneoSnooze(coordinator, "alarm_snooze"),
        ]
    )


class SomneoDismiss(SomneoEntity, ButtonEntity):
    """Dismiss alarm button."""

    _attr_translation_key = "alarm_dismiss"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_dismiss_alarm()


class SomneoSnooze(SomneoEntity, ButtonEntity):
    """Snooze alarm button."""

    _attr_translation_key = "alarm_snooze"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_snooze_alarm()
