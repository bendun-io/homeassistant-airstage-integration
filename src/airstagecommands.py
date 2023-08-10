import requests
import json

import logging
_LOGGER = logging.getLogger(__name__)


# header authority: "https://bke.euro.airstagelight.com/apiv1" -> "bke.euro.airstagelight.com"

def _getStatus(resp):
    try:
        return resp.status_code
    except AttributeError:
        return resp.status
    except Exception as e:
        raise e

async def login(baseUrl, email, password, country, language, deviceToken, ssid, *, requestModule=requests):
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

    req = await requestModule.post(baseUrl + "/users/sign_in", json=theData, headers=theHeader)
    
    stat = _getStatus(req)
    if stat != 200:
        _LOGGER.error(f'Login failed: {req.stat}\nReq Header:{theHeader}\nRequest Data: {theData}\nResponse Header: {req.headers}\nContent: {str(req.raw)}')
        return None

    return await req.json()


async def refreshToken(baseUrl, authData, *, requestModule=requests):
    authority = baseUrl.split("//")[1].split("/")[0]

    theHeader = {
        "authority": authority,
        "accept": ": application/json, text/plain, */*",
        'authorization': f'Bearer {authData["accessToken"]}',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Android SDK built for x86 Build/RSR1.210210.001.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
        'content-type': 'application/json',
        'x-requested-with': 'com.fujitsu_general.ACL_O_App',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    theData = {"user": {
                "refreshToken": authData["refreshToken"],
                }
            }

    req = await requestModule.post(baseUrl + "/users/me/refresh_token", json=theData, headers=theHeader)
    
    stat = _getStatus(req)
    if stat != 200:
        _LOGGER.error(f'Token refresh failed: {req.stat}\nReq Header:{theHeader}\nRequest Data: {theData}\nResponse Header: {req.headers}\nContent: {str(req.raw)}')
        return None

    return await req.json()


async def tryRefreshed(baseUrl, authData, *, requestModule=requests, tryFunc=lambda _:None):
    tokenRefresh = refreshToken(baseUrl, authData, requestModule=requestModule)
    if refreshToken == None:
        return None
    authData["accessToken"] = tokenRefresh["accessToken"]
    secondAttempt = json.loads(await tryFunc(authData))
    if secondAttempt==None:
        return None
    secondAttempt["newAccessToken"] = authData["accessToken"]
    return json.dumps(secondAttempt)


async def getDevices(baseUrl, authData, *, requestModule=requests, freshToken=False):
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

    req = await requestModule.get(baseUrl + "/devices/all?limit=100", data={"limit":100}, headers=theHeader)

    status = _getStatus(req)
    if status != 200:
        if not freshToken:
            secondTryFunc=lambda ad: getDevices(baseUrl, ad, requestModule=requestModule, freshToken=True)
            return tryRefreshed(baseUrl, authData, requestModule=requestModule, tryFunc=secondTryFunc)
        
        _LOGGER.error(f'Device listing failed: {status}\nReq Header:{theHeader}\nResponse Header: {req.headers}\nContent: {str(req.raw)}')
        return None
    
    return await req.json()

async def stateChange(baseUrl, authData, deviceId, parameterChange, *, requestModule=requests, freshToken=False):
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

    req = await requestModule.post(baseUrl + url, json=theData, headers=theHeader)

    status = _getStatus(req)
    if status != 200:
        # TODO implement refresh token mechanism here
        _LOGGER.error(f'Device status change failed: {status}\nHeader: {req.headers}\nContent: {req.raw}')
        return None
    
    return await req.json()


OPMODE_AUTO = "0"
OPMODE_COOL = "1"
OPMODE_DRY = "2"
OPMODE_FAN = "3"
OPMODE_HEAT = "4"

async def changeOpMode(baseUrl, authData, deviceId, targetOpMode, *, requestModule=requests):  
    return await stateChange(baseUrl, authData, deviceId, [{"name":"iu_op_mode", "desiredValue": targetOpMode}] )

async def turn_on(baseUrl, authData, deviceId, *, requestModule=requests):
    return await stateChange(baseUrl, authData, deviceId, [{"name": "iu_onoff", "desiredValue": "1"}])

async def turn_off(baseUrl, authData, deviceId, *, requestModule=requests):
    return await stateChange(baseUrl, authData, deviceId, [{"name": "iu_onoff", "desiredValue": "0"}])
