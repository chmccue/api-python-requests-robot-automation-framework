from wms.page_objects.core_functions import core_functions

from wms.payloads.fc_lpn_payloads import *




class fc_lpn_objects(core_functions):
    '''
    classdocs
    '''
    
    def fc_lpn_getSiblingList_invalid_lpn(self):
        self.check_payload_contains_values(payload=fc_lpn_pl_getSiblingList_invalid, main_keys=['error'],
                                            key_value_dict=[{"code": 500, "data": None}])
    
    def fc_lpn_getSiblingList_valid_lpn(self):
        self.check_payload_contains_values(payload=fc_lpn_pl_getSiblingList_valid, main_keys=['result', 'lpnData'],
                                            key_value_dict=[{"administratorID": 00}])

    def fc_lpn_get_valid_lpn(self):
        self.check_payload_contains_values(payload=fc_lpn_pl_get_valid, main_keys=['result', 'data'],
                                            key_value_dict=[{"action": "Shipment"}])

    def fc_lpn_get_invalid_lpn(self):
        self.check_payload_contains_values(payload=fc_lpn_pl_get_invalid, main_keys=['error'],
                                            key_value_dict=[{"code": 500, "message": "Lpn was not found", "data": None}])
        

