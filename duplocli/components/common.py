import os
import sys
import time
import json
import click
import requests
from os.path import expanduser
home = expanduser("~")

CONFIG_FILE = home + "/duplocli.config"
DUPLO_PREFIX = "duploservices-"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def getNameWithPrefix(name, tenant):
    if not name.startswith(DUPLO_PREFIX + tenant) :
        name = DUPLO_PREFIX + tenant + "-" + name 
    return name
        
def CheckEmptyParam(key, value, errmsg):
    if not value:
        raise click.BadParameter('{} cannot be empty. {}'.format(key, errmsg))

def GetConnection():
    with open(CONFIG_FILE) as json_file:
        json_data = json.load(json_file)
        tenant = json_data["DUPLO_TENANT_NAME"];
        token = json_data["DUPLO_TOKEN"];
        url = json_data["DUPLO_URL"];
        tenantId = json_data["DUPLO_TENANT_ID"];
        return tenant, token, url, tenantId
    
    return None, None, None, None
        
# Check if the tenant name and API key is set
def CheckAndGetConnection():
    tenant, token, url, tenantId = GetConnection()

    if tenant is None:
        raise click.BadParameter("Tenant Name is not set, call 'duplocli connect' to set session credentials")

    if url is None:
        raise click.BadParameter("URL is not set, call 'duplocli connect' to set session credentials")  
    
    if token is None:
        raise click.BadParameter("Token is not set, call 'duplocli connect' to set session credentials")
        
    # Login to Duplo and get tenants
    if tenantId is None:
        tenantId = validateTenantAccess(tenant, token, url) 
    return tenant, token, url, tenantId

def validateTenantAccess(tenant, token, url, tenantId=None):
    if tenantId is not None:
         return tenantId

    url = url + "/admin/GetTenantsForUser"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'content-type': 'application/json' }
    r = requests.get(url, headers=headers)
    processStatusCode(r)

    json_data = json.loads(r.text)
    tenants = []
    for index, item in enumerate(json_data):
        if item["AccountName"] == tenant:
            return item["TenantId"]
        tenants.append(item["AccountName"])
        
    raise ValueError('You do not have access to tenant {} You only have access to tenants : {}'.format(tenant, ','.join(tenants)))

def checkAndCreateS3Bucket(name, tenant, token, url, tenantId):
    
    name = getNameWithPrefix(name, tenant)

    resourcesUrl = url + "/subscriptions/" + tenantId + "/GetCloudResources"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal}
    r = requests.get(resourcesUrl, headers=headers) 
    processStatusCode(r)
    
    json_data = json.loads(r.text)
    for index, item in enumerate(json_data):
        if item["ResourceType"] == 1 :
            if item["Name"].startswith(name) :
                print("Found the s3 bucket {}".format(item["Name"]))
                return item["Name"]

    # create the bucket as it is missing
    print('Creating S3 bucket {}'.format(name))
    s3bucketurl = url + "/subscriptions/" + tenantId + "/S3BucketUpdate"
    data = {'Name': name, "Type":"1"}
    lJsonData = json.dumps(data)
    r = requests.post(s3bucketurl, data=lJsonData, headers=headers)
    processStatusCode(r)

    print('Created S3 Bucket.. sleeping for 45 seconds since a new s3 bucket at times needs that much time to be available... If file upload fails due to access denied, try again in a minute')
    # sleep for sometime
    time.sleep(30)
    return name

def createLambdaFunction(token, url, tenantId, funcObject):
    data = json.dumps(funcObject)
    newFuncUrl = url + "/subscriptions/" + tenantId + "/CreateLambdaFunction"
    
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'content-type': 'application/json' }
    r = requests.post(newFuncUrl, data=data, headers=headers)
    processStatusCode(r)

def updateLambdaFunctionCode(token, url, tenantId, data):
    data = json.dumps(data)
    newFuncUrl = url + "/subscriptions/" + tenantId + "/UpdateLambdaFunction"
    print data
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'Content-Type': 'application/json' }
    r = requests.post(newFuncUrl, data=data, headers=headers)
    processStatusCode(r)

def updateLambdaFunctionConfig(token, url, tenantId, funcObject):
    data = json.dumps(funcObject)
    print data
    newFuncUrl = url + "/subscriptions/" + tenantId + "/UpdateLambdaFunctionConfiguration"
    
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'content-type': 'application/json' }
    r = requests.post(newFuncUrl, data=data, headers=headers)
    processStatusCode(r)

    print('Updated Lambda Function {}'.format(funcObject["FunctionName"]))

def deleteLambdaFunction(token, url, tenantId, name):
    delFuncUrl = url + "/subscriptions/" + tenantId + "/DeleteLambdaFunction/" + name
    
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'content-type': 'application/json' }
    r = requests.post(delFuncUrl, data=None, headers=headers)
    processStatusCode(r)

def listLambdaFunctions(tenant, token, url, tenantId):
    resourcesUrl = url + "/subscriptions/" + tenantId + "/GetLambdaFunctions"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal}
    r = requests.get(resourcesUrl, headers=headers) 
    processStatusCode(r)
    data = json.loads(r.text)
    formattedData = json.dumps(data, indent=4, sort_keys=True)
    print(formattedData)

def createApiGatewayApi(token, url, tenantId, funcObject):
    data = json.dumps(funcObject)
    newFuncUrl = url + "/subscriptions/" + tenantId + "/ApiGatewayRestApiUpdate"
    
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'content-type': 'application/json' }
    r = requests.post(newFuncUrl, data=data, headers=headers)
    processStatusCode(r)

def deleteApiGatewayApi(token, url, tenantId, funcObject):
    data = json.dumps(funcObject)
    delFuncUrl = url + "/subscriptions/" + tenantId + "/ApiGatewayRestApiUpdate"
    
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'content-type': 'application/json' }
    r = requests.post(delFuncUrl, data=data, headers=headers)
    processStatusCode(r)

def getCloudResources(tenant, token, url, tenantId):
    resourcesUrl = url + "/subscriptions/" + tenantId + "/GetCloudResources"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal}
    r = requests.get(resourcesUrl, headers=headers) 
    processStatusCode(r)
    data = json.loads(r.text)
    return data            


def getHosts(tenant, token, url, tenantId):
    resourcesUrl = url + "/subscriptions/" + tenantId + "/GetNativeHosts"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal}
    r = requests.get(resourcesUrl, headers=headers) 
    processStatusCode(r)
    data = json.loads(r.text)
    formattedData = json.dumps(data, indent=4, sort_keys=True)
    print(formattedData)
    return data

def getMinions(tenant, token, url, tenantId):
    resourcesUrl = url + "/subscriptions/" + tenantId + "/GetMinions"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal}
    r = requests.get(resourcesUrl, headers=headers) 
    processStatusCode(r)
    data = json.loads(r.text)
    formattedData = json.dumps(data, indent=4, sort_keys=True)
    print(formattedData)
    return data


def processStatusCode(r):
    if r.status_code == 401: 
        printError('***** Unauthorized. Login again using duplocli connection connect command ')
        sys.exit()
    
    try:
        r.raise_for_status()
    except:
        printError(r.text)
        sys.exit()    

def printError(msg) :
    print(bcolors.FAIL + "FAILURE: **** " + msg +  bcolors.ENDC)  

def printSuccess(msg) :
    print(bcolors.OKGREEN + "SUCCESS: ++++ " + msg +  bcolors.ENDC)  

def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}

def remove_empty_from_dict(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.iteritems() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d