import json
import requests
import urllib3
import getpass
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generateSessionToken(vManageMgmtIp, vManagePort, username, password):
    jSessionId = genrateSessionId(vManageMgmtIp, vManagePort, username, password)
    csrfToken = generateCsrfToken(vManageMgmtIp, vManagePort, jSessionId)
    return jSessionId, csrfToken

def genrateSessionId(vManageMgmtIp, vManagePort, username, password):
    # Taking arguments as vManage IP, TCP Port number, Username and Password, this function generates the Session ID

    url = "https://" + str(vManageMgmtIp) + ":" + str(vManagePort) + "/j_security_check"
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded'
    }
    requestBody = "j_username=" + str(username) + "&j_password=" + str(password)
    response = requests.post(url, headers=headers, data = requestBody, verify=False)
    cookie = ""
    if response.status_code == 200 and response.cookies:
        for param in response.cookies:
            cookie = param.name + "=" + param.value
        return cookie
    else:
        print("Could not generate Session ID")
        exit(0)

def generateCsrfToken(vManageMgmtIp, vManagePort, jSessionId):
    # Taking arguments as vManage IP, TCP Port number and sessionId, this function generates the Cross-Site Request Forgery (CSRF) token

    url = "https://" + str(vManageMgmtIp) + ":" + str(vManagePort) + "/dataservice/client/token?json=true"
    headers = {
        'Cookie' : jSessionId,
        'Accept' : 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200 and response.headers['Content-Type'] == "application/json" :
        return response.json()['token']
    else:
        print("Could not generate CSRF Token")
        exit(0)

def getDeviceList(vManageMgmtIp,vManagePort,jSessionId):
    # Taking arguments as vManage IP, TCP Port number and sessionId, this function generates the list of devices added in the vManage

    url = "https://" + str(vManageMgmtIp) + ":" + str(vManagePort) + "/dataservice/system/device/vedges"
    headers = {
        'Cookie' : jSessionId,
        'Content-Type' : 'application/json',
        'Accept' : 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    jsonResponse = response.json()
    deviceList = jsonResponse["data"]
    return deviceList

def invalidateDevices(vManageMgmtIp, vManagePort, jSessionId, csrfToken, devicesToInvalidate):
    # Taking arguments as vManage IP, TCP Port number, sessionId, CSRF Token and a list of Device details, this function marks the device as Invalid in vManage

    url = "https://" + str(vManageMgmtIp) + ":" + str(vManagePort) + "/dataservice/certificate/save/vedge/list"
    headers = {
        'Cookie' : jSessionId,
        'X-XSRF-TOKEN' : csrfToken,
        'Content-Type' : 'application/json',
        'Accept' : 'application/json'
    }
    requestBody = json.dumps(devicesToInvalidate)
    response = requests.post(url, headers=headers, data = requestBody, verify=False)
    if response.status_code == 200:
        taskSucceeded = pushDeviceList(vManageMgmtIp, vManagePort, jSessionId, csrfToken)
        if taskSucceeded == True:
            print("\nSuccessfully marked the Devices Invalid and syced the controllers\n")

def pushDeviceList(vManageMgmtIp, vManagePort, jSessionId, csrfToken):
    # Taking arguments as vManage IP, TCP Port number, sessionId, and CSRF Token, this function pushes the changes to all controllers and monitors the status of the task

    url = "https://" + str(vManageMgmtIp) + ":" + str(vManagePort) + "/dataservice/certificate/vedge/list?action=push"
    headers = {
        'Cookie' : jSessionId,
        'X-XSRF-TOKEN' : csrfToken,
        'Content-Type' : 'application/json',
        'Accept' : 'application/json'
    }
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        taskId = response.json()['id']      
        taskSucceeded = False
        while(True):
            url = "https://" + str(vManageMgmtIp) + ":" + str(vManagePort) + "/dataservice/device/action/status/" + taskId
            headers = {
                'Cookie' : jSessionId,
                'X-XSRF-TOKEN' : csrfToken,
                'Content-Type' : 'application/json',
                'Accept' : 'application/json'
            }
            response = requests.get(url, headers=headers, verify=False)
            statusData = response.json()['data']
            deviceCount = len(statusData)
            successSync = 0
            for individualDevice in statusData:
                print(individualDevice['system-ip'] + '\t' + individualDevice['device-type'] + '\t' + individualDevice['status'])
                if individualDevice['status'] == 'Success':
                    successSync = successSync + 1
            if successSync == deviceCount:
                taskSucceeded = True
                break
            print('\nWaiting for 3 seconds...')
            time.sleep(3)
        return taskSucceeded
    return False

def deleteVedge(vManageMgmtIp, vManagePort, jSessionId, csrfToken, chassisId):
    # Taking arguments as vManage IP, TCP Port number, sessionId, CSRF Token and Chassis ID, this function deletes the device from the vManage
    
    url = "https://" + str(vManageMgmtIp) + ":" + str(vManagePort) + "/dataservice/system/device/" + chassisId
    headers = {
        'Cookie' : jSessionId,
        'X-XSRF-TOKEN' : csrfToken,
        'Content-Type' : 'application/json',
        'Accept' : 'application/json'
    }
    response = requests.delete(url, headers=headers, verify=False)
    return response.json()

def main():

    # Get vManage Login Details
    vManageMgmtIp = input('vManage IP: ')
    vManagePort = "8443"
    username = input('Username: ')
    password = getpass.getpass('Password: ')

    # Login to vManage
    jSessionId, csrfToken = generateSessionToken(vManageMgmtIp, vManagePort, username, password)

    # Get WAN Edge Device List
    deviceList = getDeviceList(vManageMgmtIp,vManagePort,jSessionId)

    devicesToInvalidate = []
    for device in deviceList:
        if  'system-ip' not in device:
            deviceDetail = {}
            deviceDetail['chasisNumber'] = device['chasisNumber']
            deviceDetail['serialNumber'] = device['serialNumber']
            deviceDetail['validity'] = 'invalid'
            devicesToInvalidate.append(deviceDetail)
    if len(devicesToInvalidate) != 0:
        invalidateDevices(vManageMgmtIp, vManagePort, jSessionId, csrfToken, devicesToInvalidate)

    # Get WAN Edge Device List
    deviceList = getDeviceList(vManageMgmtIp,vManagePort,jSessionId)

    for device in deviceList:

        if (device['chasisNumber'].find('/')):
            device['chasisNumber'] = device['chasisNumber'].replace('/', '%2F')  

        # If the device is in Invalid state, delete it
        if device['validity'] == 'invalid':
            deleteVedge(vManageMgmtIp, vManagePort, jSessionId, csrfToken, device['chasisNumber'])
            print("Deleted - " + device['chasisNumber'])

if __name__=="__main__":
    main()
