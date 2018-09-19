'''
Created on Dec 12, 2017

@author: Arun Bijapur
'''
import httplib


APIRegion='eastus.api.cognitive.microsoft.com'
subScriptionKey1 = "e5062c708f5f4450aeaeb7220c9552e9"
subScriptionKey2 = "f5bc8efcc6e3413191caa1075c248077"


class APICore(object):
    pass

    def invokeAPI(self, apiMethod, apiUrl, body):
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subScriptionKey1,
        }
       
        try:
            conn = httplib.HTTPSConnection(APIRegion)
            conn.request(apiMethod, apiUrl, str(body), headers)
            response = conn.getresponse()
            data = response.read()
            #print(data)
            conn.close()
            return data
        except Exception as e:
            print("[Error no {0}] {1}".format(e.errno, e.strerror))
            
