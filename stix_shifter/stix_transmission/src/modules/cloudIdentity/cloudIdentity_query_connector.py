from ..base.base_query_connector import BaseQueryConnector
import json
import uuid
import datetime
from .....utils.error_response import ErrorResponder

class CloudIdentityQueryConnector(BaseQueryConnector): 
    def __init__(self, api_client):
        self.api_client = api_client

    def create_query_connection(self, query):


        #print(json.loads(query))

        response = self.api_client.create_search(query)
        response_code = response.code
        response_dict = json.loads(response.read())


        # Construct a response object
        return_obj = dict()

        if response_code == 200:
            return_obj['success'] = True
            return_obj['search_id'] = response_dict['search_id']
        else:
            ErrorResponder.fill_error(return_obj, response_dict, ['message'])
        print(return_obj)
        return return_obj
        