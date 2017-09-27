import requests, sys, traceback, re, json
from pprint import pprint

from hamcrest import assert_that, matches_regexp, not_
from wms.page_objects.test_setup import base_url, custom_headers



class core_functions(object):
    
    def get_payload_results(self, payload, payload_headers=custom_headers, base_url=base_url, json_format=True):
        print "SENDING REQUEST TO " + base_url
        print "HEADERS ENTERED:"
        pprint(payload_headers)
        print "____________________\n"
        print "PAYLOAD ENTERED:"
        pprint(payload)
        with requests.Session() as s:
            if json_format == True:
                r = s.post(base_url, json=payload, headers=payload_headers).json()
            else: r = s.post(base_url, json=payload, headers=payload_headers).text
            #r = s.post(base_url, json=payload, headers=payload_headers).json()
            print "\nPAYLOAD RETURNED:"
            pprint(r)
            print "____________________\n"
            return r



    def get_specific_values_in_json(self, json_data, json_keypath=[]):
        '''
        json_data - the json data to use for parsing.
        json_keypath - main keys in the json data path to filter through. It should return the json data
        that contains the specific data you are hoping to find. This function only returns the data with 
        the given path you provide (in list format).
        
        How it fits together:
        get_specific_values_in_json(json_data={'result': {'data':[{'id':0}, {'id':1}]}}, 
                                    json_keypath=['result', 'data'])
        
        This builds a path in the json as the following: json_data['result']['data'], which returns [{'id':0}, {'id':1}].
        With this data, you can then move forward with other functions that check for specific data in the returned
        data.                                    
        '''

        count_keys = len(json_keypath)
                
        try:
            if count_keys != 0:
                if count_keys == 1:
                    get_key_value = json_data[json_keypath[0]]
                elif count_keys == 2:
                    get_key_value = json_data[json_keypath[0]][json_keypath[1]]
                elif count_keys == 3:
                    get_key_value = json_data[json_keypath[0]][json_keypath[1]][json_keypath[2]]
                elif count_keys == 4:
                    get_key_value = json_data[json_keypath[0]][json_keypath[1]][json_keypath[2]][json_keypath[3]]
            
            elif count_keys == 0:
                get_key_value = json_data
        
        except (KeyError, AttributeError, TypeError):
            get_key_value = None
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "The key path you entered was not found in the Payload returned data. Please review your key path and Payload returned data.\n"
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))            
            print("it appears the key you searched for was not found in the returned payload.")
        
        return get_key_value

            
                
    def assert_actual_vs_expected(self, act_value, exp_value, escape_regex_chars=True, exact_regex_match=False):
        '''
        Documentation: Takes a value such as a string to search against a regular expression.
        To search for a specific regex value input into exp_value, set "escape_regex_chars" to False:
        escape_regex_chars=False.
        '''
        exp_value_str = str(exp_value)
        act_value_str = str(act_value)
        print "  actual value: " + act_value_str
        print "expected value: " + exp_value_str
        if escape_regex_chars == True:
            exp_value_regex = re.escape(exp_value_str)
        else:
            exp_value_regex = exp_value_str
        
        if exact_regex_match == False:
            regex_str_final = str("(?i)"+exp_value_regex)
        else:
            regex_str_final = str("(?i)^( )?"+exp_value_regex+"$")
        try:
            assert_that(act_value_str, matches_regexp(regex_str_final))

            if exact_regex_match == False:
                print "PASS: actual value contains the expected value.\n____________________\n"
            else:
                print "PASS: actual value exactly matches the expected value.\n____________________\n"
        except AssertionError:
            if exact_regex_match == False:
                print "#####FAIL#####: actual value is not found or not contained in expected value: "
            else:
                print "#####FAIL#####: actual value is not found or does not exactly match the expected value: "
            print str(act_value) + ", " + str(exp_value) + "\n____________________\n"
            raise AssertionError

    def assert_entered_term_not_found(self, data_to_search, query, escape_regex_chars=True):
        '''
        Documentation: Takes a value such as a string to search against a regular expression.
        data_to_search should not match exp_value.
        To search for a specific regex value input into query, set "escape_regex_chars" to False:
        escape_regex_chars=False.
        '''
        exp_value_str = str(query)
        act_value_str = str(data_to_search)
        print "      Data entered: " + act_value_str
        print "Should not contain: " + exp_value_str
        if escape_regex_chars == True:
            exp_value_regex = re.escape(exp_value_str)
        else:
            exp_value_regex = exp_value_str
        regex_str_final = str("(?i)"+exp_value_regex)
        try:
            assert_that(act_value_str, not_(matches_regexp(regex_str_final)))
            
            print "actual value is not found or does not contain the expected value.\n____________________\n"
        except AssertionError:
            print "actual value is found to contain expected value: " + str(data_to_search) + ", " + str(query) + "\n____________________\n"
            raise AssertionError
    


    def check_payload_contains_values_regex(self, payload, payload_headers=custom_headers, run_payload_post=True, 
                                      main_keys=[], escape_regex_chars=True, exact_regex_match=False,
                                       key_value_dict=[]):

        '''
        Documentation: Takes a dictionary of key/value pairs wrapped in an array and checks for the pairs.
         payload: JSON/Dictionary object. NOTE THAT THIS WILL CURRENTLY ONLY WORK IN DICTIONARY STYLE JSON
         FORMAT. IT WILL NOT WORK IN NESTED LISTS AT THIS TIME. FOR NESTED LIST VALIDATION, USE 
         CHECK_PAYLOAD_CONTAINS_VALUES FUNCTION.
         
         THE DIFFERENCE BETWEEN THIS FUNCTION AND CHECK_PAYLOAD_CONTAINS_VALUES IS THAT THIS FUNCTION WILL VALIDATE 
         SPECIFIC KEY VALUE PAIRS ONE BY ONE, WHILE THE OTHER ONE WILL MAKE SURE AN ENTERED DICTIONARY IS MATCHED 
         IN THE PAYLOAD DICTIONARY. THE OTHER FUNCTION IS MORE SCALABLE, BUT THIS IS STILL WORTH SAVING AS IT MAY BE
         BETTER SUITED FOR CERTAIN API TESTS CASES.
         
         payload:
             dictionary.
             required argument.
             Payload details to enter. If the payload does not need to be sent as a request, the payload 
             entered will be used for any validations.
         
         payload_headers: 
             type: dictionary.
             optional argument.
             defaults to customer headers for this project. 
             Header details to pass to the payload for sending a request. If the payload does not need to be 
             sent as a request, payload_headers does not need to be sent.
         
         run_payload-post:
             type: boolean.
             optional argument.
             defaults to True.
             Will send the payload and payload_headers and retrieve a response. If set to False, the payload 
             entered will be checked. This is helpful if you need to check different parts of a payload without 
             having to resend a request.
         
         main_keys:
             type: array.
             optional argument.
             defaults to empty array.
             Path to filter json payload and find data to check in. For example, if the json data is expected to 
             be in a path of result > data, then enter the following: ['result', 'data'].
             The test will parse out each list item in the order it is entered in the array.
    
         escape_regex_chars:
             type: boolean.
             optional argument.
             defaults to True.
             Escapes regular expression characters entered into payload.
             
         exact_regex_match:
             type: boolean.
             optional argument.
             defaults to False.
             If set to True, will match the regular expression pattern entered exactly. If set to False, will only
             check that the entered pattern is matched somewhere in the entered validation data.
         
         key_value_dict: 
             type: array.
             optional argument (but more of a required argument, as nothing will be checked if it's empty).
             defaults to empty array.
             Takes an array that has nested dictionary items of key/value pairs the user wants to assert are present 
             in the entered payload argument. This currently does not support entering multiple dictionaries in the 
             argument, as it is not set up to iterate through nested lists/dictionary data at this time.
        '''
        get_data = {}
        get_value = ''
        fail_count = 0

        try:
            if run_payload_post == True:
                get_data = self.get_payload_results(payload, payload_headers)
            else:
                get_data = payload
            print "key value pairs entered for validation in payload:"
            pprint(key_value_dict)
            print "____________________\n"

            try:
                for x in key_value_dict:
                    if len(key_value_dict) == 1:
                        for key_name, exp_value in x.iteritems():
                            main_keys.append(key_name)
    
                            print "key being looked for: " + key_name
                            get_value = self.get_specific_values_in_json(json_data=get_data, json_keypath=main_keys)
                            self.assert_actual_vs_expected(get_value, exp_value, escape_regex_chars=escape_regex_chars, exact_regex_match=exact_regex_match)
                            main_keys.remove(key_name)
                    elif len(key_value_dict) > 1:
                        print "This function is not currently set up to check for multiple dictionaries passed in the key_value_dict. Use check_payload_contains_values function for that need."
                    #elif len(key_value_dict) > 1:                     
                    #    get_value = self.get_specific_values_in_json(json_data=get_data, json_keypath=main_keys)
                    #    for i in key_value_dict:
                    #        self.check_for_dictionary_match(get_value, i)

            except AssertionError:
                fail_count += 1
            if fail_count > 0:
                
                raise AssertionError("####FAIL####: it appears the actual values were not found or did not match the expected values." + 
                                     "\n____________________\n")

        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "\n"
            pprint(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
            raise ValueError("####FAIL####: it appears the key value pairs you searched for " + #str(print_values) + 
                             "were not found in the returned payload, or the actual value did not match the expected key value.\n____________________\n")
        return True


    def check_payload_contains_values(self, payload, payload_headers=custom_headers, run_payload_post=True, 
                                      main_keys=['result'], escape_regex_chars=True, case_sensitive=False,
                                       key_value_dict=[]):

        '''
        Documentation:

         payload:
             dictionary.
             required argument.
             Payload details to enter. If the payload does not need to be sent as a request, the payload 
             entered will be used for any validations.
         
         payload_headers: 
             type: dictionary.
             optional argument.
             defaults to customer headers for this project.
             Header details to pass to the payload for sending a request. If the payload does not need to be 
             sent as a request, payload_headers does not need to be sent.
         
         run_payload-post:
             type: boolean.
             optional argument.
             defaults to True.
             Will send the payload and payload_headers and retrieve a response. If set to False, the payload 
             entered will be checked. This is helpful if you need to check different parts of a payload without 
             having to resend a request.
         
         main_keys:
             type: array.
             optional argument.
             defaults to empty array.
             Path to filter json payload and find data to check in. For example, if the json data is expected to 
             be in a path of result > data, then enter the following: ['result', 'data'].
             The test will parse out each list item in the order it is entered in the array.
         
         key_value_dict: 
             type: array.
             optional argument (but more of a required argument, as nothing will be checked if it's empty).
             defaults to empty array.
             Takes an array that has nested dictionary items of key/value pairs the user wants to assert are present 
             in the entered payload argument. If multiple dictionaries are entered in the array, the function assumes
             they are part of a nested list that contains sub-dictionaries in json data and will loop through any 
             available nested dictionaries for comparison. If a comparison is found, the test passes; if no comparison
             is found, the test fails.
        '''
        get_data = {}
        get_value = ''
        fail_count = 0
        # ========================================
        # ========================================
        try:
            if run_payload_post == True:
                get_data = self.get_payload_results(payload, payload_headers)
            else:
                get_data = payload
            print "key value pairs entered for validation in payload:"
            pprint(key_value_dict)
            print "____________________\n"
            # ========================================
            # ========================================
            try:
                get_value = self.get_specific_values_in_json(json_data=get_data, json_keypath=main_keys)
                
                for i in key_value_dict:

                    self.check_for_dictionary_match(dict_to_check=get_value, dict_to_assert=i, case_sensitive=case_sensitive)

            # ========================================
            # ========================================
            except AssertionError:
                fail_count += 1
            if fail_count > 0:
                
                raise AssertionError("####FAIL####: it appears the actual values were not found or did not match the expected values." + 
                                     "\n____________________\n")

        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "\n"
            pprint(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
            raise ValueError("####FAIL####: it appears the key value pairs you searched for " + #str(print_values) + 
                             "were not found in the returned payload, or the actual value did not match the expected key value.\n____________________\n")
        return True


    def check_payload_contains_values_as_string(self, payload, payload_headers=custom_headers, run_payload_post=True, 
                                      escape_regex_chars=True, case_sensitive=False,
                                       key_value_dict=[]):
        '''DOCUMENTATION: This works by converting the payload and values to check into strings and doing a blanket
        search within the payload. It is not as specific as using the other value checker, as that will check specific 
        areas of the JSON data by entering main keys to use as a path into the JSON data.
        This may be ok for general checks, but as it is more of a blanket checker, it may not be as useful as the more 
        specific one. I recommend using this when you have JSON in multiple layers that you need to check with one 
        request being sent, as no filtering is needed for this function.'''
        pass

    def convert_json_data_to_lowercase(self, json_data):
        # dict to str
        str_json = json.dumps(json_data)
        str_json_lowercase = str_json.lower()
        # str to dict
        dict_from_str_json = json.loads(str_json_lowercase)
        return dict_from_str_json

    def check_for_dictionary_match(self, dict_to_check, dict_to_assert, case_sensitive=False):

        if case_sensitive == False:
            item2_ready = self.convert_json_data_to_lowercase(dict_to_assert).viewitems()
        else: item2_ready = dict_to_assert.viewitems()
        check_value = False
        if type(dict_to_check) is list:
            '''Assumption: this is a list that has nested dictionaries in it, 
                which can be iterated through and checked for validation.'''
            for result in dict_to_check:
                check_value = False
                
                if case_sensitive == False:
                    item1_ready = self.convert_json_data_to_lowercase(result).viewitems()
                elif case_sensitive == True:
                    item1_ready = result.viewitems()
    
                if item2_ready <= item1_ready:
                    print "PASS: " + str(item2_ready) + " was matched in nested payload.\n"
                    check_value = True
                    break
        
        elif type(dict_to_check) is dict:
            if case_sensitive == False:
                item1_ready = self.convert_json_data_to_lowercase(dict_to_check).viewitems()
            elif case_sensitive == True:
                item1_ready = dict_to_check.viewitems()
                
            if item2_ready <= item1_ready:
                print "PASS: " + str(item2_ready) + " was matched in nested payload.\n"
                check_value = True
            
        if check_value == False:
            print "####FAIL####: " + str(dict_to_assert) + " not found in payload."
            raise AssertionError


    def check_for_no_dictionary_match(self, dict_to_check, dict_to_assert, case_sensitive=False):

        if case_sensitive == False:
            item2_ready = self.convert_json_data_to_lowercase(dict_to_assert).viewitems()
        else: item2_ready = dict_to_assert.viewitems()
        check_value = False
        if type(dict_to_check) is list:
            '''Assumption: this is a list that has nested dictionaries in it, 
                which can be iterated through and checked for validation.'''
            for result in dict_to_check:
                check_value = False
                
                if case_sensitive == False:
                    item1_ready = self.convert_json_data_to_lowercase(result).viewitems()
                elif case_sensitive == True:
                    item1_ready = result.viewitems()
    
                if item2_ready <= item1_ready:
                    print "####FAIL####: " + str(item2_ready) + " was matched in nested payload.\n"
                    check_value = True
                    break
        
        elif type(dict_to_check) is dict:
            if case_sensitive == False:
                item1_ready = self.convert_json_data_to_lowercase(dict_to_check).viewitems()
            elif case_sensitive == True:
                item1_ready = dict_to_check.viewitems()
            
    
            if item2_ready <= item1_ready:
                print "####FAIL####: " + str(item2_ready) + " was matched in nested payload.\n"
                check_value = True
            
        if check_value == True:
            print "####FAIL####: " + str(dict_to_assert) + " was found in payload, but wasn't expected to."
            raise AssertionError


    def check_payload_does_not_contain_dictionary(self, payload, payload_headers=custom_headers, run_payload_post=True, 
                                      main_keys=[], escape_regex_chars=True, case_sensitive=False,
                                       key_value_dict=[]):

        '''
        Documentation: Takes a dictionary of key/value pairs and checks they are not present.
         
         payload:
             dictionary.
             required argument.
             Payload details to enter. If the payload does not need to be sent as a request, the payload 
             entered will be used for any validations.
         
         payload_headers: 
             type: dictionary.
             optional argument.
             defaults to customer headers for this project. 
             Header details to pass to the payload for sending a request. If the payload does not need to be 
             sent as a request, payload_headers does not need to be sent.
         
         run_payload-post:
             type: boolean.
             optional argument.
             defaults to True.
             Will send the payload and payload_headers and retrieve a response. If set to False, the payload 
             entered will be checked. This is helpful if you need to check different parts of a payload without 
             having to resend a request.
         
         main_keys: key paths as strings in list format. For example, if the json data is expected to be in a
         path of result > data, then enter the following: ['result', 'data'].
         The test will parse out each list item in the order it is given and look for the key from the 
         **key_value_dict key in order to get the value from the expected key.
         
         key_value_dict: Takes a dictionary of key/value pairs wrapped in an array the user wants to assert are 
         present in the entered payload argument. For example: {"hello":"world", "id":1} will first verify that 
         the key "hello" has the value "world", and then will verify that the key value "id" has the value 1.
        '''
        get_data = {}
        get_value = ''
        fail_count = 0
        # ========================================
        # ========================================
        try:
            if run_payload_post == True:
                get_data = self.get_payload_results(payload, payload_headers)
            else:
                get_data = payload
            print "key value pairs entered that should not match payload:"
            pprint(key_value_dict)
            print "____________________\n"
            # ========================================
            # ========================================
            try:
                get_value = self.get_specific_values_in_json(json_data=get_data, json_keypath=main_keys)
                
                for i in key_value_dict:

                    self.check_for_no_dictionary_match(dict_to_check=get_value, dict_to_assert=i, case_sensitive=case_sensitive)

            # ========================================
            # ========================================
            except AssertionError:
                fail_count += 1
            if fail_count > 0:
                
                raise AssertionError("####FAIL####: it appears the actual values were not found or did not match the expected values." + 
                                     "\n____________________\n")

        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "\n"
            pprint(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
            raise ValueError("####FAIL####: it appears the key value pairs you searched for " + #str(print_values) + 
                             "were not found in the returned payload, or the actual value did not match the expected key value.\n____________________\n")
        return True


##### NOT YET COMPLETED.
    def verify_terms_not_present(self, payload, payload_headers=custom_headers, run_payload_post=True, 
                                      escape_regex_chars=True, terms_to_check=['error', '404', '500']):
        '''
        Documentation: Similar to check_payload_does_not_contain_values, except searches all payload to make
        sure entered items are not found anywhere in it. The aforementioned keyword attempts to search for 
        a specific key to get the value in it and makes its comparison there, in a more isolated part of the 
        payload. This keyword is a more general form of "this entered phrase is not found in it anywhere".
        Takes a dictionary of key/value pairs.

         payload:
             dictionary.
             required argument.
             Payload details to enter. If the payload does not need to be sent as a request, the payload 
             entered will be used for any validations.
         
         payload_headers: 
             type: dictionary.
             optional argument.
             defaults to customer headers for this project.
             Header details to pass to the payload for sending a request. If the payload does not need to be 
             sent as a request, payload_headers does not need to be sent.
         
         run_payload-post:
             type: boolean.
             optional argument.
             defaults to True.
             Will send the payload and payload_headers and retrieve a response. If set to False, the payload 
             entered will be checked. This is helpful if you need to check different parts of a payload without 
             having to resend a request.
         
         terms_to_check:
             type: array.
             optional argument.
             defaults to common error terms.
             Takes an array of terms the user wants to assert are not present in the entered payload argument. 
             For example: ['error', '404'] will first verify that the first item "error" is not present in the 
             payload, and then will verify that the next term "404" is not present, etc. This is not as specific
             as the other function written for this similar purpose, which checks that a dictionary is not present
             in the payload dictionary, but can be useful if you are certain a term is not supposed to be present 
             anywhere in the payload, in keys or values.
        '''
        get_data = {}
        fail_count = 0
        
        if len(terms_to_check) <= 0:
            raise Exception("No key/value pairs were found in the key_value_dict argument. There's nothing for the method to search for and verify. " +
            "Please make sure a dictionary of key/value pair are entered in the following format: {'key1':'value1', 'key2':'value2'}.\n____________________\n")
        
        try:
            if run_payload_post == True:
                get_data = self.get_payload_results(payload, payload_headers)
            else:
                get_data = payload
            print "The payload should not contain the following term(s):"
            pprint(terms_to_check)
            print "____________________\n"
            
            # dict to str
            json_as_str = json.dumps(get_data)
            
            for term in terms_to_check:
                try:
                    self.assert_entered_term_not_found(str(json_as_str), str(term), escape_regex_chars=escape_regex_chars)
                    
                except AssertionError:
                    fail_count += 1
                    print "The term " + str(term) + " was found in the payload you searched: " + str(get_data)
            if fail_count > 0:
                raise AssertionError("####FAIL####it appears a term you searched for was found in the payload.\n____________________\n")

        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "\n"
            pprint(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
            #raise ValueError
            print("it appears the term or terms you searched for were not found in the payload.\n____________________\n")
        return True
    
    



