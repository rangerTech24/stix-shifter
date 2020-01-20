# Developing Cloud Identity Transmission Module

[STIX-adapter-guide](../../../../../adapter-guide/develop-stix-adapter.md)


## Prerequisites for Transmission Call
- Python 3.6 is required to use stix-shifter
- Running Cloud Identity Instance
- Authentication Objects: Connection Object - Configuration Object

## Transmit Introduction
Transmit offers several functions: `ping`, `query`, `results`.

The purpose of this guide is to show the steps in creating the Transmission Module for Cloud Identity.  Each of the transmit functions takes in common arguments: the connection object, and the configuration object.  Each of the [CLI commands](#Available-Commands) can be run in the terminal in the stix-shifter root directory.  

### Transmission call template
```
python main.py transmit cloudIdentity <Connection Object> <Configuration Object> <results,ping, query> <Query> <offset> <length>
```

#### Connection Object
```
{
    "host": <Host Url or IP addres>,
    "port": <Port> optional
}
```

#### Configuration Object
```
{
    "auth": {
        "tenant": <Tenant>,
        "clientId": <clientId>,
        "clientSecret": <clientSecret>
    }
}
```
#### Query Example
```
"[userid = '23442342'] FROM (start-time) t'2020-01-01T12:24:01.009Z' TO (end-time)  t'2020-01-06T12:54:01.009Z'"
```
**Note: If FROM and TO are not given the request searches past 24 hours**



## Cloud Identity Transmission Files
| Folder/file                 | Why is it important? Where is it used?                                  |
   | --------------------------- | ----------------------------------------------------------------------- |
   | **init**.py                 | This file is required by Python to properly handle library directories. |
   | apiclient.py                | This file contains all REST api Calls to Cloud Identity. |
   | cloudIdentiy_connector.py    | Initalizes cloudIdentity_*_connector.py files. connector files listed below |
   | cloudIdentity_results_connector.py | This file takes in search_id, offset, and length. Calls apiclient.py and returns results based on input parameters | 
   | cloudIdentity_ping.py | This file verifies that the Cloud Identity Tenant is running |
   | cloudIdentity_query_connector.py | This file takes in translated STIX query and initalizes search_id. |
   | cloudIdenity_status_connector.py | 

### Available-Commands

#### Ping

Using configuration object - test if a access token can be initalized

##### CLI COMMAND

`python main.py transmit cloudIdentity '<CONNECTION OBJECT>' '<CONFIGURATION OBJECT>' ping`


##### OUTPUT

`{'success': True}`


#### Query 

Uses Cloud Identity API to submit a query to the connection

##### CLI COMMAND

`python main.py transmit cloudIdentity '<CONNECTION OBJECT>' '<CONFIGURATION OBJECT>' query <CLOUD IDENTITY QUERY>`

##### OUTPUT

`{ 'success' : True, 'search_id' : <SEARCH ID> }`


#### Results

Uses Cloud Identity API to fetch the query results.  Because Cloud Identity is report driven application, the use of report API's are used to gather information.  Report API's currently implemented are `auth_audit_trail`, `app_audit_trail`, and `user_activity`.  In cases where the `userid` or `username` are present in query, a call to `getUser(userid)` or `getUserWithFilter(username)` are used along with reports listed above. 

##### CLI COMMAND

`python main.py transmit cloudIdentity '<CONNECTION OBJECT>' '<CONFIGURATION OBJECT>' results <SEARCH_ID> <OFFSET> <LENTH>`

##### OUTPUT

`{ 'success' : True, 'data' : [<QUERY RESULTS>] }`

**NOTE: Before the QUERY RESULTS are sent to the translation modules the JSON response from Cloud Identity has to be refined.  This is done to make the translation code readable and simple to implement.  Results Example below**

#### Results Example

##### Cloud Identity Query 
**Note**: Translated in Translation Module

`[username = 'test-username'] FROM t'2020-01-01T12:24:01.009Z' TO t'2020-01-06T12:54:01.009Z'`

**Transmit Query**
```
python3 main.py transmit cloudIdentity '{"host": "Host Name", "port": "Host Port"}' '{"auth": {"tenant": "tenantUrl", "clientId": "tenant ID", "clientSecret": "Client Secret"}}' results "[username = '1234567'] FROM t'2020-01-01T12:24:01.009Z' TO t'2020-01-06T12:54:01.009Z'" 1 1
```
##### Transmission Steps

1. stix-shifter main.py calls `cloudIdentity_results_connector.py` 

2. `cloudIdentity_results_connector.py` module: 

    - Creates a `search_id`.  

        **Note**: In the connectors final deployment, the search_id is initialized when the `cloudIdentity_query_connector.py` is called.  For testing purposes the search_id is created here.

    - Calls `apiclient.get_search_results(search_id, offset, length)` to acquire search results 

3. `apiclient.get_search_results` parses the query and initalizes the request parameters and the request payload
    - Request Parameters:
    ```
    {
        username = 'test-username'
    }
    ```
    - Request Payload:
    ```
    {
        "FROM": '2020-01-01T12:24:01.009Z',
        "TO": '2020-01-06T12:54:01.009Z',
        "SORT_BY": "time",     //Default payload parameter
        "SORT_ORDER": "asc",   //Default payload parameter
        "SIZE": 1 //Length field in request
        "USERNAME": 'test-username'
    }
    ```
4. `get_search_results` then calls `call_reports(request_params)` to call all reports
5. `call_reports` calls each individual report passing the request_params with it. 
    1. `user_activity`
    2. `app_audit_trail`
    3. `auth_audit_trail`

    **Note**: Each report returns a different JSON response
6. Example API call for `auth_audit_trail`:
    - Using Payload and Parameters in step 3, Cloud Identity's response: 
    ```
    {'response': {'report': {'hits': [{'_id': 'df2ff27f-f962-448f-a5ee-5a482805bf88',
                                    '_index': 'event-authentication-2020.1-000001',
                                    '_source': {'data': {'origin': '71.65.247.60',
                                                            'realm': 'https://w3id.sso.ibm.com/auth/sps/samlidp2/saml20',
                                                            'result': 'success',
                                                            'subject': '650003TBP0',
                                                            'subtype': 'federation',
                                                            'username': 'test-username'},
                                                'geoip': {'country_iso_code': 'US',
                                                            'country_name': 'United '
                                                                            'States',
                                                            'region_name': 'North '
                                                                            'Carolina'},
                                                'time': 1578075021506},
                                    '_type': 'doc',
                                    'sort': [1578075021506,
                                                'df2ff27f-f962-448f-a5ee-5a482805bf88']}],
                            'total': 5}},
    'success': True}
    ```
    - Because the JSON path to the information is complex, `auth_audit_trail` will then refine the JSON object down to:
    ```
    {'data': {'origin': '71.65.247.60',
          'realm': 'https://w3id.sso.ibm.com/auth/sps/samlidp2/saml20',
          'result': 'success',
          'subject': '650003TBP0',
          'subtype': 'federation',
          'username': 'test-user'},
    'geoip': {'country_iso_code': 'US',
           'country_name': 'United States',
           'region_name': 'North Carolina'},
    'time': 1578075021506}
    ``` 
    **Note**: Each report refines the JSON object appropriately 

7. After each report send a request, all reports are merged together to create a report with all useful data

8. The data is then returned back to `cloudIdentity_results_connecter.py` as a response object that will then be interpretted by the Cloud Identity Translation Module




