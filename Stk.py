
from datetime import datetime

import base64
import MySQLdb
import MySQLdb.cursors
import logging
import eventlet
import hashlib
import requests
import logging
import base64
from requests.auth import HTTPBasicAuth
import json

from datetime import datetime

from stk_configs import logger, config, mysql_params, service, endpoint
from expiringdict import ExpiringDict

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

cache = ExpiringDict(max_len=1, max_age_seconds=3500)

class Stk():
    def authentication(self):
        """
        Generate access token/fetch from cache
        """
        access_token = ""
        if not cache.get("access_token"):
            url = get(endpoint['authentication'])
            querystring = {"grant_type":"client_credentials"}
            payload = ""
            headers = {
                'Authorization': "Basic 1223",
                'cache-control': "no-cache",
                'Postman-Token': "123234"
                }
            response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
            access_token = json.loads(response.text)['access_token']
        else:
            access_token = cache.get("access_token")  
            print access_token
        return access_token

    def encrypt_sp_password (self, timestamp):
        """
        spPassword = BASE64(SHA-256(spId + Password + timeStamp))
        """
        m = hashlib.sha256()
        #m.update(mpesa_params['merchant_id'] + mpesa_params['pass_key'] + timestamp)
        #return base64.b64encode(m.hexdigest())
        return base64.b64encode(service['shortcode'] + service['pass_key'] + timestamp)



    def stk_push(self, amount, msisdn, account_no, transaction_desc):
        access_token = self.authentication() 
	#print 'Test', access_token
        
        timestamp = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
        password =self.encrypt_sp_password(timestamp)

	#print password

        headers = { 
            "Authorization": "Bearer %s" % access_token,
            "Content-Type" : "application/json"
        }
        
        request = {}
        request['BusinessShortCode'] = service['shortcode']
        request['Password'] = password
        request['Timestamp'] = timestamp
        request['TransactionType'] = service['transaction_type']
        request['Amount'] = int(amount)
        request['PartyA'] = msisdn
        request['PartyB'] = service['shortcode']
        request['PhoneNumber'] = msisdn
        request['CallBackURL'] = endpoint['result_endpoint']
        request['AccountReference'] = account_no
        request['TransactionDesc'] = transaction_desc
	
        print request
        
        r = requests.post(endpoint['stkpush_api'], json = request, headers=headers, verify = False)
        print json.loads(r.text)
        return json.loads(r.text)

    def stk_push_query(self, checkoutRequestID):
        access_token = self.authentication()
        timestamp = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
        password = get(endpoint['password'])
        headers = { "Authorization": "Bearer %s" % access_token }
        request = {
            "BusinessShortCode": service['shortcode'],
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkoutRequestID
        }

        r = requests.post(endpoint['stkpushquery_api'], json = request, headers=headers)

        return json.loads(r.text)  
