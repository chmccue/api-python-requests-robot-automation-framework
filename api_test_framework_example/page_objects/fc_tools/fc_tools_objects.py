from wms.page_objects.core_functions import core_functions
from wms.payloads.fc_tools_payloads import *


class fc_tools_objects(core_functions):
    
    def fc_tools_check_for_latest_WMS_version_on_server(self):
        self.check_payload_contains_values_regex(payload=fc_tools_pl_getiWMSVersion, main_keys=['result'], key_value_dict=[{'wmsVersion': '2.3.'}])
