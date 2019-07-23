import requests
from requests.auth import HTTPBasicAuth
import json
import ssl
import logging
import httplib

# Debug logging
httplib.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
req_log = logging.getLogger('requests.packages.urllib3')
req_log.setLevel(logging.DEBUG)
req_log.propagate = True


consumer_key = "gjGJkotGx4mPlV0sqI9AlpVO3mpwWtwG"
consumer_secret = "2ruDkSq5h6b5Zdax"
api_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

#r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret),  verify='/usr/local/lib/stkpush/chain.pem')
r = requests.request("GET", api_URL, auth=(consumer_key, consumer_secret), verify=False)
print r
#response = json.loads(r.text)
#print (response['access_token'])

url = "https://api.safaricom.co.ke/oauth/v1/generate"

querystring = {"grant_type":"client_credentials"}

#headers = {
 #   'Authorization': "Basic N2lGckFtRHBySko1clM5azlKVGFHWjhTbTJrSGI4cjg6VU5LTEszYm0xaEkwdGJsMA==",
  #  'Cache-Control': "no-cache",
   # 'Postman-Token': "78f960d2-8074-45f3-b071-2521d2eef861"
    #}

response = requests.request("GET", url, auth=(consumer_key, consumer_secret), params=querystring, verify=False)

print(response.text)

