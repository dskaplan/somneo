"""A entity class for Somneo integration."""
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SomneoCoordinator


class SomneoEntity(CoordinatorEntity[SomneoCoordinator]):
    """Somneo entity class."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SomneoCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        entry = coordinator.config_entry
        dev_info = entry.data["dev_info"]
        self._attr_unique_id = f"{entry.unique_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            manufacturer=dev_info["manufacturer"],
            model=f"{dev_info['model']} {dev_info['modelnumber']}",
            name=entry.data[CONF_NAME],
        )


class SomneoWakeupEntity(SomneoEntity):
    """Entity for a setting of the wake-up alarm."""

    _key: str

    def __init__(self, coordinator: SomneoCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, f"wakeup_{key}")
        self._attr_translation_key = f"wakeup_{key}"
        self._key = key

    @property
    def _value(self) -> object | None:
        """Return the value of the setting."""
        return self.coordinator.data["wakeup"].get(self._key)

    @property
    def available(self) -> bool:
        """Return if the setting is known."""
        return super().available and self._value is not None
