from ..base.base_ping import BasePing
import json
from .....utils.error_response import ErrorResponder


class CloudIdentityPing(BasePing):
    def __init__(self, api_client):
        self.api_client = api_client

    def ping(self):
        response = self.api_client.ping()
        response_code = response.code

        response_dict = json.loads(response.read())
    
        return_object = dict()
        return_object['success'] = False
        
        if len(response_dict) > 0 and response_code == 200:
            return_object['success'] = True
            #return_obj["search_id"] = response_dict.get('search_id',"NA")
        else:
            ErrorResponder.fill_error(return_object, response_dict, ['message'])
            
        return return_object
    