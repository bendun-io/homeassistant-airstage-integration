""" Fujistsu Cloud Airstage Integration """
from __future__ import annotations

import asyncio
import logging
_LOGGER = logging.getLogger(__name__)

from aiohttp import ClientConnectionError
from async_timeout import timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_TOKEN, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession


from .const import DOMAIN, CONF_BASEURL
from .airstagedevice import AirstageDevice
from .airstageaccount import AirStageAccount

PLATFORMS = [Platform.CLIMATE]  # , Platform.SENSOR


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Establish connection with Airstage."""
    conf = entry.data

    asc = AirStageAccount(conf[CONF_USERNAME], conf[CONF_PASSWORD], conf[CONF_BASEURL], conf[CONF_TOKEN] )
    airstage_devices = await airstage_devices_setup(hass, asc )
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


async def airstage_devices_setup(
    hass: HomeAssistant, account: AirStageAccount
) -> list[AirstageDevice]:
    """Query connected devices from Airstage."""
    
    account.setRequestModule(async_get_clientsession(hass))
    try:
        async with timeout(10):
            all_devices = await account.getDevices()
    except (asyncio.TimeoutError, ClientConnectionError) as ex:
        raise ConfigEntryNotReady() from ex

    return [AirstageDevice(device) for device in all_devices]