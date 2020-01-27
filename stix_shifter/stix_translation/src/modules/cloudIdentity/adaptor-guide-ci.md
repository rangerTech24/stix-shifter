# Developing Cloud Identity Translation Modules

[STIX-adapter-guide](../../../../../adapter-guide/develop-stix-adapter.md)

## Prerequistes 
- Your development environment must use Python 3.6.
- You must have access to the target data source.
- Access to Cloud Identity API's.
- You must be familiar or understand the following concepts:
 - Observable objects: See [STIX™ Version 2.0. Part 4: Cyber Observable Objects](http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part4-cyber-observable-objects.html)
 - Stix patterning. See [STIX™ Version 2.0. Part 5: STIX Patterning](https://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part5-stix-patterning.html)



## Introduction 

The purpose of this guide is to show the steps in creating the Translation Module for Cloud Identity.  

## Steps used for implementation:
1. Translate STIX Query
2. Transit Query to Cloud Identity. These steps are in [Transmission Adaptor Guide](../../../../stix_transmission/src/modules/cloudIdentity/develope-ci-adapter.md)
3. Translate Cloud Identity Response

