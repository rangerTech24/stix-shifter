# Developing Cloud Identity Transmission Module

[STIX-adapter-guide](../../../../../adapter-guide/develop-stix-adapter.md)


## Introduction
The purpose of this guide is to show the steps in creating the Transmission Module for Cloud Identity.  

## Prerequisites
- A running Cloud Identity Instance
- To authenticate Cloud Identity Instance a Connection and Configuration object are required
- In order for a response from Cloud Identity a request query is required - this query is created in the Cloud Identity Translation Module


### Connection Object
```
{
    "host": <Host Url or IP addres>,
    "port": <Port> optional
}
```

### Configuration Object
```
{
    "auth": {
        "tenant": <Tenant>,
        "clientId": <clientId>,
        "clientSecret": <clientSecret>
    }
}
```
### Example Query
```
"[userid = '23442342'] FROM (start-time) TO (end-time)"
```



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

## Command Line Example

```
python3 main.py transmit cloudIdentity '{"host": "Host Name", "port": "Host Port"}' '{"auth": {"tenant": "tenantUrl", "clientId": "tenant ID", "clientSecret": "Client Secret"}}' results "STIX Translated Query" offset=Integer Value length=Integer Value
```
