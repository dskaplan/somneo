"""Support for Philips Somneo devices."""
from __future__ import annotations

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF_SESSION, ENTITY_KEYS
from .coordinator import SomneoConfigEntry, SomneoCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.MEDIA_PLAYER,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
]


async def async_setup_entry(hass: HomeAssistant, entry: SomneoConfigEntry) -> bool:
    """Set up the Somneo component."""
    coordinator = SomneoCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    entry.async_on_unload(entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SomneoConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(hass: HomeAssistant, entry: SomneoConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: SomneoConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", entry.version)

    if entry.version < 4:
        data = {**entry.data}
        data.pop("options", None)
        data.pop("use_session", None)
        hass.config_entries.async_update_entry(
            entry, data=data, options={CONF_SESSION: True}, version=4
        )

    if entry.version < 5:
        # Version 5 replaced the entities of the 16 alarms by a single wake-up
        # alarm and dropped the sunset, PowerWake and display entities.
        registry = er.async_get(hass)
        prefix = f"{entry.unique_id}_"
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
            if entity.unique_id.removeprefix(prefix) not in ENTITY_KEYS:
                registry.async_remove(entity.entity_id)
        hass.config_entries.async_update_entry(entry, version=5)

    _LOGGER.info("Migration to version %s successful", entry.version)

    return True
