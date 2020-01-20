# Developing Cloud Identity Transmission Module

[STIX-adapter-guide](../../../../../adapter-guide/develop-stix-adapter.md)


## Introduction
The purpose of this guide is to show the steps in creating the Transmission Module for Cloud Identity.

## Cloud Identity Transmission Files
| Folder/file                 | Why is it important? Where is it used?                                  |
   | --------------------------- | ----------------------------------------------------------------------- |
   | **init**.py                 | This file is required by Python to properly handle library directories. |
   | apiclient.py                |
   | async_dummy_connector.py    |
   | async_dummy_error_mapper.py |

## Command Line Example

```
python3 main.py transmit cloudIdentity '{"host": "Host Name", "port": "Host Port"}' '{"auth": {"tenant": "tenantUrl", "clientId": "tenant ID", "clientSecret": "Client Secret"}}' results "STIX Translated Query" offset=Integer Value length=Integer Value
```
