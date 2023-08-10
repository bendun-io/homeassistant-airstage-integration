
import logging
_LOGGER = logging.getLogger(__name__)

from .airstagecommands import stateChange
from .airstagecommands import OPMODE_AUTO, OPMODE_COOL, OPMODE_DRY, OPMODE_FAN, OPMODE_HEAT

const = {
    "OPERATION_MODE_HEAT": OPMODE_HEAT,
    "OPERATION_MODE_DRY": OPMODE_DRY,
    "OPERATION_MODE_COOL": OPMODE_COOL,
    "OPERATION_MODE_FAN_ONLY": OPMODE_FAN,
    "OPERATION_MODE_HEAT_COOL": OPMODE_AUTO
}


class AirstageAC():

    def __init__(self, deviceinfo, baseurl, authData) -> None:
        self.baseurl  = baseurl
        self.authData = authData

        self.device_data = deviceinfo
        self.name = deviceinfo["deviceName"]    # this one may not be needed as it is configurable TODO CHECK
        self.serial = deviceinfo["deviceId"]
        self.mac = None # deviceinfo.mac        # TODO see if it is needed
        self.device_info = f'The Fujitsu AC with serial number {self.serial}'

        self.operation_modes = [OPMODE_AUTO, OPMODE_COOL, OPMODE_DRY, OPMODE_FAN, OPMODE_HEAT]
        self.operation_mode = None
        self.power = False

        self.fan_speeds = []                # TODO see if that is needed
        self.fan_speed = None
        
        self.room_temperature = None
        self.target_temperature = None
        self.target_temperature_min = None
        self.target_temperature_max = None
        self.temperature_increment = 0.5
        

    async def update(self):
        pass # TODO

    async def set(self, set_dict):
        params = []
        if "power" in set_dict:
            params.append({"name": "iu_onoff", "desiredValue": "1" if set_dict["power"] else "0"})
        if "target_temperature" in set_dict:
            pass                            # TODO !!
            self.target_temperature = set_dict["target_temperature"] # maybe first change and validate, then update
        if "fan_speed" in set_dict:
            pass                            # TODO check, see above
        if "operation_mode" in set_dict:
            params.append({"name":"iu_op_mode", "desiredValue": set_dict['operation_mode']})

        rslt = stateChange(self.baseurl, self.authData, self.serial, params)
        
        if rslt == None:
            raise Exception(f'Cannot set state {set_dict} to device {self.serial}')


from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, MIN_TIME_BETWEEN_UPDATES
from homeassistant.util import Throttle
from aiohttp import ClientConnectionError
from async_timeout import timeout
from typing import Any


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