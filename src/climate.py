"""Platform for climate integration."""
from __future__ import annotations

# from datetime import timedelta
from typing import Any

from pymelcloud import DEVICE_TYPE_ATA, DEVICE_TYPE_ATW, AtaDevice, AtwDevice # TODO create this ata field in the Airstage device
import voluptuous as vol
import airstagedevice.const as ata

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AirstageCloudClimate
from .const import (
    DOMAIN,
)

# SCAN_INTERVAL = timedelta(seconds=60)


ATA_HVAC_MODE_LOOKUP = {
    ata.OPERATION_MODE_HEAT: HVACMode.HEAT,
    ata.OPERATION_MODE_DRY: HVACMode.DRY,
    ata.OPERATION_MODE_COOL: HVACMode.COOL,
    ata.OPERATION_MODE_FAN_ONLY: HVACMode.FAN_ONLY,
    ata.OPERATION_MODE_HEAT_COOL: HVACMode.HEAT_COOL,
}
ATA_HVAC_MODE_REVERSE_LOOKUP = {v: k for k, v in ATA_HVAC_MODE_LOOKUP.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Airstage device climate based on config_entry."""
    airstage_devices = hass.data[DOMAIN][entry.entry_id] # TODO check this one
    entities: list[AirstageCloudClimate] = [
        AirstageCloudClimate(airstage_device)
        for airstage_device in airstage_devices
    ]
    
    async_add_entities(
        entities,
        True,
    )


class AirstageCloudClimate(ClimateEntity):
    """Air-to-Air climate device."""


    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, device) -> None:
        """Initialize the climate."""
        self.api = device
        self._base_device = self.api.device
        """Initialize the climate."""
        # self._device = ata_device

        self._attr_name = device.name
        self._attr_unique_id = f"{self.api.device.serial}-{self.api.device.mac}"

    async def async_update(self) -> None:
        """Update state from AirstageCloud."""
        await self.api.async_update()

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self.api.device_info

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return self._base_device.temperature_increment


    _attr_supported_features = (
        ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TARGET_TEMPERATURE
        # | ClimateEntityFeature.SWING_MODE
    )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode."""
        mode = self._base_device.operation_mode
        if not self._base_device.power or mode is None:
            return HVACMode.OFF
        return ATA_HVAC_MODE_LOOKUP.get(mode)

    def _apply_set_hvac_mode(
        self, hvac_mode: HVACMode, set_dict: dict[str, Any]
    ) -> None:
        """Apply hvac mode changes to a dict used to call _device.set."""
        if hvac_mode == HVACMode.OFF:
            set_dict["power"] = False
            return

        operation_mode = ATA_HVAC_MODE_REVERSE_LOOKUP.get(hvac_mode)
        if operation_mode is None:
            raise ValueError(f"Invalid hvac_mode [{hvac_mode}]")

        set_dict["operation_mode"] = operation_mode
        if self.hvac_mode == HVACMode.OFF:
            set_dict["power"] = True

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        set_dict: dict[str, Any] = {}
        self._apply_set_hvac_mode(hvac_mode, set_dict)
        await self._base_device.set(set_dict)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes."""
        return [HVACMode.OFF] + [
            ATA_HVAC_MODE_LOOKUP[mode]
            for mode in self._base_device.operation_modes
            if mode in ATA_HVAC_MODE_LOOKUP
        ]

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._base_device.room_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._base_device.target_temperature

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        set_dict: dict[str, Any] = {}
        if ATTR_HVAC_MODE in kwargs:
            self._apply_set_hvac_mode(
                kwargs.get(ATTR_HVAC_MODE, self.hvac_mode), set_dict
            )

        if ATTR_TEMPERATURE in kwargs:
            set_dict["target_temperature"] = kwargs.get(ATTR_TEMPERATURE)

        if set_dict:
            await self._base_device.set(set_dict)

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        return self._base_device.fan_speed

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        await self._base_device.set({"fan_speed": fan_mode})

    @property
    def fan_modes(self) -> list[str] | None:
        """Return the list of available fan modes."""
        return self._base_device.fan_speeds


    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self._base_device.set({"power": True})

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self._base_device.set({"power": False})

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        min_value = self._base_device.target_temperature_min
        if min_value is not None:
            return min_value

        return DEFAULT_MIN_TEMP

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        max_value = self._base_device.target_temperature_max
        if max_value is not None:
            return max_value

        return DEFAULT_MAX_TEMP

    # async def async_set_vane_horizontal(self, position: str) -> None:
    #     """Set horizontal vane position."""
    #     if position not in self._device.vane_horizontal_positions:
    #         raise ValueError(
    #             f"Invalid horizontal vane position {position}. Valid positions:"
    #             f" [{self._device.vane_horizontal_positions}]."
    #         )
    #     await self._device.set({ata.PROPERTY_VANE_HORIZONTAL: position})

    # async def async_set_vane_vertical(self, position: str) -> None:
    #     """Set vertical vane position."""
    #     if position not in self._device.vane_vertical_positions:
    #         raise ValueError(
    #             f"Invalid vertical vane position {position}. Valid positions:"
    #             f" [{self._device.vane_vertical_positions}]."
    #         )
    #     await self._device.set({ata.PROPERTY_VANE_VERTICAL: position})

    # @property
    # def swing_mode(self) -> str | None:
    #     """Return vertical vane position or mode."""
    #     return self._device.vane_vertical

    # async def async_set_swing_mode(self, swing_mode: str) -> None:
    #     """Set vertical vane position or mode."""
    #     await self.async_set_vane_vertical(swing_mode)

    # @property
    # def swing_modes(self) -> list[str] | None:
    #     """Return a list of available vertical vane positions and modes."""
    #     return self._device.vane_vertical_positions