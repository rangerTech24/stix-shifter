from ..utils.RestApiClient import RestApiClient
from ..utils.RestApiClient import ResponseWrapper
from requests.models import Response
import base64
import urllib.parse
import pprint
import json, requests
import re
import datetime
import time
from calendar import timegm



class APIClient():
    
    def __init__(self, connection, configuration):
        
        self.connection = connection
        self.configuration = configuration
        self.headers = dict()
        self.search_id = None
        self.query = None 
        self.authorization = None
        self.credentials = None
        self.headers = dict()

        self.client = RestApiClient(host=connection.get('host'), 
                                    port=connection.get('port', None))
        #Init connections
        client_id = configuration.get('auth').get("clientId", None)
        client_secret = configuration.get('auth').get("clientSecret", None)
        tenant = configuration.get('auth').get('tenant', None)
        self.token = configuration.get('auth').get('token', None)

        #Init host/port
        host = connection.get('host')
        port = connection.get('port', None)

        #TODO enable a proxy to connect to Cloud Identity
        if(client_id is not None and client_secret is not None and tenant is not None):
            self.credentials = {"tenant": tenant, "client_id": client_id, "client_secret": client_secret}
            self.token = self.getToken()
        else: 
            self.credentials = None           
            raise IOError ("Cloud Identity Credentials not provided in connection/configuration")

        #Init communication to Cloud Identity Tenant
        

        # Init base headers
        self._add_headers('Accept', "application/json, text/plain, */*")
        self._add_headers("Content-Type", "application/json")

    # Searches both reports and events from Cloud Identity 
    def run_search(self, query_expression):
        #Run search on Cloud identity reports  
        report_response = self.search_reports(query_expression)
        
        return report_response

    def ping(self):
        respObj = Response()
        if (self.getToken()):
            respObj.code = "200"
            respObj.error_type = ""
            respObj.status_code = 200
            content = '{"status":"OK", "data": {"message": "Service is up."}}'
            respObj._content = bytes(content, 'utf-8')
        else:
            respObj.code = "503"
            respObj.error_type = "Service Unavailable"
            respObj.status_code = 503
            content = '{"status":"Failed", "data": {"message": "Service is down."}}'
            respObj._content = bytes(content, 'utf-8')
        # return
        return ResponseWrapper(respObj)

    def create_search(self, query_expression):
        # Queries the data source
        respObj = Response()
        
        if(self.getToken()):
            self.query = query_expression
            response = self.build_searchId()
            
            if (response != None):
                respObj.code = "200"
                respObj.error_type = ""
                respObj.status_code = 200
                content = '{"search_id": "' + \
                    str(response) + \
                    '", "data": {"message":  "Search id generated."}}'
                respObj._content = bytes(content, 'utf-8')
            else:
                respObj.code = "404"
                respObj.error_type = "Not found"
                respObj.status_code = 404
                respObj.message = "Could not generate search id."
        else:
            respObj.error_type = "Unauthorized: Access token could not be generated."
            respObj.message = "Unauthorized: Access token could not be generated."

        return ResponseWrapper(respObj)

    def get_search_status(self, search_id):
        # Check the current status of the search
        return {"code": 200, "search_id": search_id, "status": "COMPLETED"}

    def get_search_results(self, search_id, offset=None, length=None):
        # Return the search results. Results must be in JSON format before being translated into STIX

        pp = pprint.PrettyPrinter(indent=1)
        payload = self.format_payload(search_id, length)
        
        
        print(payload)
        return_obj = dict()

        resp = self.call_reports(payload)
        return resp
        
    # Supports Cloud Identity's main report calls:  
    # User_activity - Application Audit Trail - Authentication Audit Trial
    def call_reports(self, payload):
        return_obj = dict()
        # 1) search user_activity 
        #user_activity = self.get_user_activity(request_params)

        # 2) search application audit reports
        #app_audit = self.get_app_audit(payload)
    
        # 3) search authentication audit reports
        user_auth = self.get_auth_audit(payload)

        return user_auth

    def delete_search(self, search_id):
        # Optional since this may not be supported by the data source API
        # Delete the search
        return "Deleted query: {}".format(search_id)

    def set_searchId(self, search_id):
        self.search_id = search_id
        return

    def build_searchId(self):
        #       It should be called only ONCE when transmit query is called
        # Structure of the search id is
        # '{"query": ' + json.dumps(self.query) + ', "credential" : ' + json.dumps(self.credential) + '}'
        s_id = None

        if(self.query is None or self.authorization is None or self.credentials is None):
            raise IOError(3001, 
            "Could not generate search id because 'query' or 'authorization token' or 'credential info' is not available.")
#
        else:
            id_str = '{"query": ' + json.dumps(self.query) + ', "credential" : ' + json.dumps(self.credentials) + '}'
            
            id_byt = id_str.encode('utf-8')
            s_id = base64.b64encode(id_byt).decode()
            self.set_searchId(s_id)

        return s_id

    def decode_searchId(self):
        # These value (self.credential, self.query) must be present.  self.authorization may not.
        try:
            id_dec64 = base64.b64decode(self.search_id)
            jObj = json.loads(id_dec64.decode('utf-8'))
        except:
            raise IOError(
                3001, "Could not decode search id content - " + self.search_id)
#
        self.query = jObj.get("query", None)
        self.credentials = jObj.get("credentials", None)
        self.authorization = jObj.get("authorization", None)
        
        return

    #NOTE All functions below are either Cloud Identity REST calls or modifier functions 

    def get_credentials(self):
        if self.credentials is None:
            raise IOError("Cloud Identity Credential object is None")
        else: 
            data = self.credentials

        return data

    #Retrieve valid token from Cloud Identity
    def getToken(self):

        success = False
        if(self.authorization is not None):
            if (self.isTokenExpired((self.authorization).get("expiresTimestamp"))):
                success = True 
                self._addAuthHeader()
                return success

        
        if(self._getToken()):
            success = True
            self._addAuthHeader()

        return success

    def _getToken(self):
        success = False

        auth = self.get_credentials()

        options = {
            "client_id": auth.get("client_id"),
            "client_secret": auth.get("client_secret"),
            "grant_type": "client_credentials"
        }

        endpoint = "v2.0/endpoint/default/token"

        time = datetime.datetime.now()
        resp = self.client.call_api(endpoint, "POST", data=options)
        jresp = json.loads(str(resp.read(), 'utf-8')) 

        if(resp.code != 200):
            raise ValueError(str(jresp) + " -- Access Token not received")
        else:
            success = True
            exTime = (time + datetime.timedelta(seconds=jresp.get("expires_in"))).timestamp()
            self.authorization = json.loads('{"access_token":"' + jresp.get("access_token") + '", "expiresTimestamp":' + str(exTime) + '}')

        return success
        
    def isTokenExpired(self, exTime):
        if exTime is not None:
            if(exTime > (datetime.datetime.now()).timestamp()):
                return True
        return False

    #returns a application audit - uses filter in payload to refine search 
    def get_app_audit(self, payload):
        pp = pprint.PrettyPrinter(indent=1)

        #Set applications to all 
        payload['APPID'] = "*"
        #Remove any payload variables that arent readable by report call 
        if "username" in payload: payload.pop("PERFORMED_BY_USERNAME")
        endpoint = "/v1.0/reports/app_audit_trail"

        #Convert data to CI readable data 
        data = json.dumps(payload)

        resp = self.client.call_api(endpoint, "POST", headers=self.headers, data=data)
        jresp = json.loads(str(resp.read(), 'utf-8'))


        retList = []
        #If response has more than one return object concat each object
        if(jresp['response']['report']['total'] > 1):
            retList = self.concatData(jresp['response']['report']['hits'])
        pp.pprint(retList)
        resp = self.createResponse(resp, retList)

        return resp

    #returns and authentication audit - uses filter in payload to refine search 
    def get_auth_audit(self, payload):
        pp = pprint.PrettyPrinter(indent=1)
        #Audit payload are different for each report call so they are initialized here. (Case sensitive)

        #if "PERFORMED_BY_USERNAME" in payload: payload.pop("PERFORMED_BY_USERNAME")
        payload = payload.strip("[]")
        reg1 = r"username"
        data = re.sub(reg1, "USERNAME", payload)
        reg2 = r"client_ip"
        data = re.sub(reg2, "CLIENT_IP", data)

        endpoint = "/v1.0/reports/auth_audit_trail" 
        print(data)
        resp = self.client.call_api(endpoint, "POST", headers=self.headers, data=data)
        jresp = json.loads(resp.read())
        pp.pprint(jresp)

        retList = []
        #If response has more than one return object concat each object
        if(jresp['response']['report']['total'] > 1):
            retList = self.concatData(jresp['response']['report']['hits'])

        resp = self.createResponse(resp, retList)

        return resp

    #Get user_activity report - uses filter in payload to refine search 
    def get_user_activity(self, payload):
        pp = pprint.PrettyPrinter(indent=1)
        # If username is requested the user-activity report is looking for PERFORMED_BY_USERNAME
        if "USERNAME" in payload: payload.pop('USERNAME')

        data = json.dumps(payload)

        endpoint = "/v1.0/reports/user_activity"
 
        resp = self.client.call_api(endpoint, "POST", headers = self.headers, data=data)
        jresp = json.loads(resp.read())

        #NOTE TODO have not gotten a reponse from this yet
        #retResp = self.createResponse(resp, jresp['response']['report']['hits'][0]['_source'])
  

        return resp

    def get_admin_activity(self, payload):
        
        return

       
    def getUser(self, id):
        
        endpoint = "/v2.0/Users/" + id
        response = self.client.call_api(endpoint, 'GET', headers=self.headers)
        jresp = json.loads(str(response.read(), 'utf-8'))

        return response
    
    def getUserWithFilters(self, payload):
        endpoint = "/v2.0/Users" + self.set_filters(payload)

        response = self.client.call_api(endpoint, 'GET', headers=self.headers)
        jresp = json.loads(response.read())
        
        retResp = self.createResponse(response, jresp['Resources'][0])
        return retResp
    
    #Used to convert request parameters into scim formatted query - only works for one param as of now
    def set_filters(self, payload):
        payload.pop("TO")
        payload.pop("FROM")

        filters = urllib.parse.urlencode(payload)
        
        retFilters = re.sub("=", "%20eq%20%22", filters) + "%22"

        return "?filter=" + retFilters

    def _add_headers(self, key, value):
        self.headers[key] = value
        return

    def _addAuthHeader(self):
        auth = "Bearer " + str(self.authorization.get("access_token"))
        self._add_headers("authorization", auth)
        return


    #Format the input query into payload send to Cloud Identity
    def format_payload(self, search_id, length):
        pp = pprint.PrettyPrinter(indent=1)
        payload = search_id

        reg1 = r"'"
        out_str = re.sub(reg1, "\"", payload)
        jpayload = json.loads(out_str)
        #Set size field in payload and set username/userid to correct syntax
        for index in jpayload:
            if index.get("FROM") is not None:
                #Convert input time to epoch milliseconds
                FROM = time.strptime(index.get("FROM"), '%Y-%m-%dT%H:%M:%S.%fZ')
                index["FROM"] = timegm(FROM) * 1000
                index['SIZE'] = int(length)
            if (index.get("TO")) is not None:
                TO = time.strptime(index.get("TO"), '%Y-%m-%dT%H:%M:%S.%fZ')
                index["TO"] = timegm(TO) * 1000
            if index.get("username") is not None:
                index["username"] = "\"{}\"".format(index['username'])
            if index.get("client_ip") is not None:
                index["client_ip"] = "\"{}\"".format(index['client_ip'])

        data = json.dumps(jpayload)
        #Take }, { out of query to finalize return
        reg2 = r"}, {"
        retObj = re.sub(reg2, ", ", data)
        return retObj
        
    #Creates a new reponse - purpose is to refine json response so stix mapping is simple
    def createResponse(self, resp, newContent):
        pp = pprint.PrettyPrinter(indent=1)
        respObj = Response()
        if(resp.code == 200):
            respObj.code = "200"
            respObj.status_code = 200
            content = json.dumps(newContent) #put new content in response
            respObj._content = bytes(content, 'utf-8')
        elif(resp.code == 400):
            respObj.code = "400"
            respObj.error_type = "Bad Request"
            respObj.status_code = 400
            respObj.message = "Could not generate response."
        elif(resp.code == 500):
            respObj.code = "500"
            respObj.error_type = "Internal Server Error"
            respObj.status_code = 400
            respObj.message = "An internal server error occured. "

        return ResponseWrapper(respObj)

    #merges two json/dict objects - purpose to to create more robust stix report by adding new data
    def mergeJson(self, dict1, dict2):
        dict1.update(dict2)
        return dict1

    #Used to concatenate each response into one object
    def concatData(self, dataObj):
        retList = []
        for data in dataObj: 
            retList.append(data['_source'])
        
        return retList
