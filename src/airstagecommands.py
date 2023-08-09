import requests

import logging
_LOGGER = logging.getLogger(__name__)


#  o = i.data.firebaseDeviceToken, a = i.data.macAddress, 
# header authority: "https://bke.euro.airstagelight.com/apiv1" -> "bke.euro.airstagelight.com"

async def login(baseUrl, email, password, country, language, deviceToken, ssid):
    authority = baseUrl.split("//")[1].split("/")[0] 
    theHeader = {
        "authority": authority,
        "accept": ": application/json, text/plain, */*",
        'authorization': 'Bearer undefined',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Android SDK built for x86 Build/RSR1.210210.001.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
        'content-type': 'application/json',
        'x-requested-with': 'com.fujitsu_general.ACL_O_App',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    theData = {"user": {
                "email": email,
                "password": password,
                "country": country,
                "language": language,
                "deviceToken": deviceToken,
                "ssid": ssid, 
                "osVersion":"Android 11"}
            }

    req = requests.post(baseUrl + "/users/sign_in", json=theData, headers=theHeader)
    
    if req.status_code != 200:
        _LOGGER.error(f'Login failed: {req.status_code}\nReq Header:{theHeader}\nRequest Data: {theData}\nResponse Header: {req.headers}\nContent: {str(req.raw)}')
        return None

    return req.json()

async def getDevices(baseUrl, authData):
    authority = baseUrl.split("//")[1].split("/")[0]

    theHeader = {
        "authority": authority,
        "accept": ": application/json, text/plain, */*",
        'authorization': f'Bearer {authData["accessToken"]}',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Android SDK built for x86 Build/RSR1.210210.001.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
        'x-requested-with': 'com.fujitsu_general.ACL_O_App',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    req = requests.get(baseUrl + "/devices/all?limit=100", data={"limit":100}, headers=theHeader)

    if req.status_code != 200:
        _LOGGER.error(f'Device listing failed: {req.status_code}\nReq Header:{theHeader}\nResponse Header: {req.headers}\nContent: {str(req.raw)}')
        return None
    
    return req.json()

async def stateChange(baseUrl, authData, deviceId, parameterChange):
    authority = baseUrl.split("//")[1].split("/")[0]
    url = f'/devices/{deviceId}/set_parameters_request'

    theHeader = {
        "authority": authority,
        "accept": ": application/json, text/plain, */*",
        'authorization': f'Bearer {authData["accessToken"]}',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Android SDK built for x86 Build/RSR1.210210.001.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
        'x-requested-with': 'com.fujitsu_general.ACL_O_App',
        'content-type': 'application/json',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    theData = {
        "deviceSubId":0,
        "parameters": parameterChange
    }

    req = requests.post(baseUrl + url, json=theData, headers=theHeader)

    if req.status_code != 200:
        _LOGGER.error(f'Device listing failed: {req.status_code}\nHeader: {req.headers}\nContent: {req.raw}')
        return None
    
    return req.json()


OPMODE_AUTO = "0"
OPMODE_COOL = "1"
OPMODE_DRY = "2"
OPMODE_FAN = "3"
OPMODE_HEAT = "4"

async def changeOpMode(baseUrl, authData, deviceId, targetOpMode):  
    return await stateChange(baseUrl, authData, deviceId, [{"name":"iu_op_mode", "desiredValue": targetOpMode}] )

async def turn_on(baseUrl, authData, deviceId):
    return await stateChange(baseUrl, authData, deviceId, [{"name": "iu_onoff", "desiredValue": "1"}])

async def turn_off(baseUrl, authData, deviceId):
    return await stateChange(baseUrl, authData, deviceId, [{"name": "iu_onoff", "desiredValue": "0"}])
