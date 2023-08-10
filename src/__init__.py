""" Fujistsu Cloud Airstage Integration """
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientConnectionError
from async_timeout import timeout
# from pymelcloud import Device
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry # SOURCE_IMPORT,
from homeassistant.const import CONF_TOKEN, Platform # CONF_USERNAME, 
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo
# from homeassistant.helpers.typing import ConfigType
from homeassistant.util import Throttle

from .const import DOMAIN, CONF_BASEURL
from .airstagecommands import getDevices
from .airstagedevice import AirstageAC

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

PLATFORMS = [Platform.CLIMATE]  # , Platform.SENSOR, Platform.WATER_HEATER

# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Establish connection with Airstage."""
#     if DOMAIN not in config:
#         return True

#     username = config[DOMAIN][CONF_USERNAME]
#     token = config[DOMAIN][CONF_TOKEN]
#     hass.async_create_task(
#         hass.config_entries.flow.async_init(
#             DOMAIN,
#             context={"source": SOURCE_IMPORT},
#             data={CONF_USERNAME: username, CONF_TOKEN: token},
#         )
#     )
#     return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Establish connection with Airstage."""
    conf = entry.data

    airstage_devices = await airstage_devices_setup(hass, conf[CONF_BASEURL], conf[CONF_TOKEN])
    hass.data.setdefault(DOMAIN, {}).update({entry.entry_id: airstage_devices})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    hass.data[DOMAIN].pop(config_entry.entry_id)
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
    return unload_ok


class AirstageDevice:
    """Airstage Device instance. TODO CHECK METHODS HERE!"""

    def __init__(self, device: AirstageAC) -> None:
        """Construct a device wrapper."""
        self.device = device
        self.name = device.name
        self._available = True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self, **kwargs):
        """Pull the latest data from Airstage."""
        try:
            await self.device.update()
            self._available = True
        except ClientConnectionError:
            _LOGGER.warning("Connection failed for %s", self.name)
            self._available = False

    async def async_set(self, properties: dict[str, Any]):
        """Write state changes to the Airstage API."""
        try:
            await self.device.set(properties)
            self._available = True
        except ClientConnectionError:
            _LOGGER.warning("Connection failed for %s", self.name)
            self._available = False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def device_id(self):
        """Return device ID."""
        return self.device.device_id

    # @property # TODO check if this one is needed
    # def building_id(self):
    #     """Return building ID of the device."""
    #     return self.device.building_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        model = None
        if (unit_infos := self.device.units) is not None:
            model = ", ".join([x["model"] for x in unit_infos if x["model"]])
        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self.device.mac)},
            identifiers={(DOMAIN, f"{self.device.mac}-{self.device.serial}")},
            manufacturer="Fujitsu",
            model=model,
            name=self.name,
        )

    # @property # TODO check if this one is actually needed
    # def daily_energy_consumed(self) -> float | None:
    #     """Return energy consumed during the current day in kWh."""
    #     return self.device.daily_energy_consumed


async def airstage_devices_setup(
    hass: HomeAssistant, baseurl: str, token
) -> list[AirstageDevice]:
    """Query connected devices from Airstage."""
    
    try:
        async with timeout(10):
            all_devices = await getDevices(baseurl, token,
                                           requestModule=async_get_clientsession(hass)
                                           )
    except (asyncio.TimeoutError, ClientConnectionError) as ex:
        raise ConfigEntryNotReady() from ex

    all_devices = all_devices["devices"]

    return [AirstageDevice(AirstageAC(device, baseurl, token)) for device in all_devices]