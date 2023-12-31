
import logging
_LOGGER = logging.getLogger(__name__)

from .airstagecommands import OPMODE_AUTO, OPMODE_COOL, OPMODE_DRY, OPMODE_FAN, OPMODE_HEAT

const = {
    "OPERATION_MODE_HEAT": OPMODE_HEAT,
    "OPERATION_MODE_DRY": OPMODE_DRY,
    "OPERATION_MODE_COOL": OPMODE_COOL,
    "OPERATION_MODE_FAN_ONLY": OPMODE_FAN,
    "OPERATION_MODE_HEAT_COOL": OPMODE_AUTO
}


# from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, MIN_TIME_BETWEEN_UPDATES
from homeassistant.util import Throttle
from aiohttp import ClientConnectionError
from typing import Any


class AirstageDevice:
    """Airstage Device instance."""

    def __init__(self, device) -> None:
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

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        
        return DeviceInfo(
            # connections={(CONNECTION_NETWORK_MAC, self.device.mac)},
            identifiers={(DOMAIN, f"{self.device.serial}")},
            manufacturer="Fujitsu",
            model=self.device.model,
            sw_version=self.device.sw_version,
            name=self.name,
        )