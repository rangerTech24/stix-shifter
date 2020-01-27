# Developing Cloud Identity Translation Modules

[STIX-adapter-guide](../../../../../adapter-guide/develop-stix-adapter.md)

[Cloud Identity Transmission Adaptor Guide](../../../../stix_transmission/src/modules/cloudIdentity/develope-ci-adapter.md)

## Prerequistes 
- Your development environment must use Python 3.6.
- You must have access to the target data source.
- Access to Cloud Identity API's.
- You must be familiar or understand the following concepts:
 - Observable objects: See [STIX™ Version 2.0. Part 4: Cyber Observable Objects](http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part4-cyber-observable-objects.html)
 - Stix patterning. See [STIX™ Version 2.0. Part 5: STIX Patterning](https://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part5-stix-patterning.html)



## Introduction 

The purpose of this guide is to show the steps in creating the Translation Module for Cloud Identity.  Because Cloud Identity utilizes report based RESTful API's and does not contain a base query langauge the only available queries use `AND's` and `OR's`.  In the connectors current state, the connector can only search the Cloud Identity reports for `userid`, `username` and `client_ip`.  


## Translation Modules

| Folder/file             | Why is it important? Where is it used?                                                                                                                                                                                                                                                                     |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| json/from_stix_map.json | This mapping file is used to translate a STIX pattern to a data source query result.                                                                                                                                                                                                                       |
| json/to_stix_map.json   | This mapping file is used to translate a data source query result into STIX objects.                                                                                                                                                                                                                       |
| **init**.py             | This file is required by Python to properly handle library directories.                                                                                                                                                                                                                                    |
| data_mapping.py         | This file uses the mappings that are defined in the from_stix_map.json file to map the STIX objects and their properties to field names from the data source.                                                                                                                                              |
| cloudIdentity_translator.py     | This file contains the Translator class. It inherits the BaseTranslator abstract base class and is the interface to the rest of the translation logic.                                                                                                                                                     |
| cloudIdentity_query_constructor.py    | This file contains the QueryStringPatternTranslator class, which translates the ANTLR parsing of the STIX pattern to the native data source query.                                                                                                                                                         |
| stix_to_query.py        | This file contains the StixToQuery class, which inherits the BaseQueryTranslator class. <br><br>StixToQuery calls out to the ANTLR parser, which returns a parsing of the STIX pattern. The parsing is then passed onto the query_constructor.py where it is translated into the native data source query. |
| transformers.py         | This file is used to transform data formats as required by STIX and the native data source query language.                                                                                                                                                                                                 |
| MANIFEST.in             | This file is used by Python when packaging the library.                                                                                                                                                                                                                                                    |

## Overview of Process
1. Translate STIX Query to Cloud Identity Query,
2. Transmit Cloud Identity Query. See [Cloud Identity Transmission Adaptor Guide](../../../../stix_transmission/src/modules/cloudIdentity/develope-ci-adapter.md)
3. Translate Cloud Identity Response into STIX Bundle

## Steps for Implementation 

### Step 1: Edit the from_stix_map JSON file
The `from_stix_map.json` is used to define HOW to translate a STIX pattern to a Cloud Identity query.  STIX patterns are expressions that represent Cyber Observable Objects.  
 1. Identity the Cloud Identity source fields.
 2. In your `cloudIdentity` translation folder, go to your json/ subfolder and edit the `from_stix_map.json` file. This file contains mappings to the current STIX objects and properties supported by the Cloud Identity connector.

 #### Generic STIX Object Mapping Format:
  ```
    {
        "stix-object": {
            "fields": {
                "stix_object_property": ["DataSourceField", "DataSourceField"],
                "stix_object_property": ["DataSourceField"]
            }
        }
    }
  ```
  - Map your Cloud Identity fields to a STIX object and property. Define the mapping based on the specified format. You can map multiple data source fields to the same STIX object property. 
    - "stix-object" refer to a STIX cyber observable object type name
    - "stix_object_property" refers to a STIX cyber observable object property name

#### Example STIX Object Mapping for Cloud Identity:

The following example illustrates the mapping of STIX objects (user-account, ipv4-addr) to a Cloud Identity with the fields – userid, username, client_ip.

Reference: [from_stix_map](json/from_stix_map.json)

  ```
{
    "user-account": {
        "fields": {
            "user_id": ["userid"],
            "account_login": ["username"], 
            //More fields are in file
            }
    },
    "ipv4-addr": {
        "fields": {
                "value":["client_ip"]
            }
        }
}
  ```
 