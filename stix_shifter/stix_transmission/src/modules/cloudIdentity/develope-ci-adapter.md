# Developing Cloud Identity Transmission Module

[Reference-STIX-adapter-guide](../../../../../adapter-guide/develop-stix-adapter.md)


## Introduction
The purpose of this guide is to show the steps in creating the Transmission Module for Cloud Identity.



## Command Line Example

```
python3 main.py transmit cloudIdentity '{"host": "Host Name", "port": "Host Port"}' '{"auth": {"tenant": "tenantUrl", "clientId": "tenant ID", "clientSecret": "Client Secret"}}' results "STIX Translated Query" offset=Integer Value length=Integer Value
```
