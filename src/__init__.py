""" Fujistsu Cloud Airstage Integration """
from __future__ import annotations

import asyncio
import logging

from aiohttp import ClientConnectionError
from async_timeout import timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, Platform 
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession


from .const import DOMAIN, CONF_BASEURL
from .airstagecommands import getDevices
from .airstagedevice import AirstageAC, AirstageDevice


_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.CLIMATE]  # , Platform.SENSOR


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