from .airstagecommands import getDevices, stateChange, login
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
                self.renewAuth()
                return getDevices(self, renewedAuth=True)
            return None

        self.updateAuthDataIfNeeded(deviceList)

        return [AirstageAC(self, dev) for dev in deviceList['devices']]

    def renewAuth(self):
        _LOGGER.debug("Refresh failed, renewing login")
        _LOGGER.error("TEST")
        self.authData = login(
                        self.baseUrl, self.username, self.password, "Germany", "de", # TODO parameters, Germany and de
                        requestModule=self.requestModul
                    )

    def updateAuthDataIfNeeded(self, response):
        if hasattr(response, "newAuthData"):
            self.authData = response['newAuthData']

class AirstageAC():

    def __init__(self, account, deviceinfo) -> None:
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
        

    async def update(self): # TODO implement
        rslt = None
        if rslt == None:
            return
        
        self.account.updateAuthDataIfNeeded(rslt)

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

        self.account.updateAuthDataIfNeeded(rslt)