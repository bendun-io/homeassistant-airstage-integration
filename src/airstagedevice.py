
import logging
_LOGGER = logging.getLogger(__name__)

from .airstagecommands import login, stateChange
from .airstagecommands import OPMODE_AUTO, OPMODE_COOL, OPMODE_DRY, OPMODE_FAN, OPMODE_HEAT

const = {
    "OPERATION_MODE_HEAT": OPMODE_HEAT,
    "OPERATION_MODE_DRY": OPMODE_DRY,
    "OPERATION_MODE_COOL": OPMODE_COOL,
    "OPERATION_MODE_FAN_ONLY": OPMODE_FAN,
    "OPERATION_MODE_HEAT_COOL": OPMODE_AUTO
}

# TODO Ensure that the constructor gets the following data!
# self.device_data.baseUrl, self.device_data.authData, self.device_data.deviceid

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