from .airstagecommands import getDevices, stateChange, login, getDeviceById
from .airstagecommands import OPMODE_AUTO, OPMODE_COOL, OPMODE_DRY, OPMODE_FAN, OPMODE_HEAT

import logging
_LOGGER = logging.getLogger(__name__)

class AirStageAccount():

    def __init__(self, username, password, baseUrl, authData):
        self.username = username
        self.password = password
        self.baseUrl = baseUrl
        self.authData = authData
        self.requestModul = None

    def setRequestModule(self, requestModul):
        self.requestModul = requestModul

    async def getDevices(self, renewedAuth=False):
        deviceList = None
        if self.requestModul==None:
            deviceList = await getDevices(self.baseUrl, self.authData)
        else:
            deviceList = await getDevices(self.baseUrl, self.authData, requestModule=self.requestModul)
        
        if deviceList==None:
            if renewedAuth==False:
                await self.renewAuth()
                return await self.getDevices(renewedAuth=True)
            return None

        self.updateAuthDataIfNeeded(deviceList)

        return [AirstageAC(self, dev) for dev in deviceList['devices']]

    async def renewAuth(self):
        _LOGGER.warning("Refresh failed, renewing login")
        self.authData = await login(
                        self.baseUrl, self.username, self.password, "Germany", "de", # TODO parameters, Germany and de
                        requestModule=self.requestModul
                    )
        # TODO storage of the new auth data would be nice

    def updateAuthDataIfNeeded(self, response):
        if hasattr(response, "newAuthData"):
            self.authData = response['newAuthData']

    async def changeDeviceState(self, deviceSerial, parameters, renewedAuth=False):
        rslt = await stateChange(self.baseUrl, self.authData, deviceSerial, parameters, requestModule=self.requestModul)
        if rslt == None and not renewedAuth:
            await self.renewAuth()
            return await self.changeDeviceState(deviceSerial, parameters, renewedAuth=True)
        return rslt

    async def getDeviceState(self, deviceId, renewedAuth=False):
        rslt = await getDeviceById(self.baseUrl, self.authData, deviceId, requestModule=self.requestModul)
        if rslt == None and not renewedAuth:
            await self.renewAuth()
            return await self.getDeviceState(self, deviceId, renewedAuth=True)
        return rslt

import json

class AirstageAC():

    def __init__(self, account: AirStageAccount, deviceinfo) -> None:
        self.account = account

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

        # Used in AirstageDevice method device_info            
        self.sw_version = self._getParam("iu_main_ver")
        self.model = deviceinfo["model"] + "-" + self._getParam("iu_model")
        self._updateParamFields()

    def _getParam(self, paramName):
        return [param["value"] for param in self.device_data["parameters"] if param["name"]==paramName][0]

    def _updateParamFields(self):
        self.operation_mode = self._getParam("iu_op_mode")
        self.power = False if self._getParam("iu_onoff") == "0" else True
        self.room_temperature = (float(self._getParam("iu_indoor_tmp"))/100.0 - 32.0) * 5.0 / 9.0 # converting fahrenheit to celsius
        self.target_temperature = float(self._getParam("iu_set_tmp")) / 10

    async def update(self):
        rslt = await self.account.getDeviceState(self.serial)
        if rslt == None:
            return

        self.device_data["parameters"] = rslt["parameters"]
        self._updateParamFields()

    async def set(self, set_dict):
        _LOGGER.warn(f'called to set {json.dumps(set_dict)}')
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

        rslt = await self.account.changeDeviceState(self.serial, params)
        
        if rslt == None:
            raise Exception(f'Cannot set state {set_dict} to device {self.serial}')

        self.account.updateAuthDataIfNeeded(rslt)
        await self.update()