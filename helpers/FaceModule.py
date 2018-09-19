'''
Created on Dec 12, 2017

@author: Arun Bijapur
'''

APIRegion='westcentralus.api.cognitive.microsoft.com'

subscriptionKey1="5c288cca6d5c439fb467d2c030f0f60e"
subscriptionKey2="28634f60bda340acbc03cb8172846437"
import httplib, urllib, base64


class FaceModule(object):
    pass    
    def __init__(self):
     pass
 
    def findSimilar(self):
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscriptionKey1,
        }
        
        params = urllib.urlencode({
        })
        body={    
            "faceId":"c5c24a82-6845-4031-9d5d-978df9175426",
            "faceListId":"sample_list",  
            "maxNumOfCandidatesReturned":10,
            "mode": "matchPerson"
        }
        
        try:
            conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("POST", "/face/v1.0/findsimilars?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            
    def addFaceToFaceList(self, faceImageUrl):
    
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscriptionKey1,
        }
        
        params = urllib.urlencode({
            # Request parameters
            'userData': 'name=arunbijapur;age=30',
            'targetFace': ''
        })
        
        try:
            conn = httplib.HTTPSConnection(APIRegion)
            conn.request("POST", "/face/v1.0/facelists/1234/persistedFaces?%s" % params, "{ url:"+faceImageUrl+"}", headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
        
    
    def createFaceList(self):
     ########### Python 2.7 #############
   
       
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscriptionKey1,
        }
        
        params = urllib.urlencode({
        })
        
        body={
                "name":"naoBeBranchFaces",
                "userData":""
            }
        try:
            conn = httplib.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
            conn.request("PUT", "/face/v1.0/facelists/1234?%s" % params, str(body), headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}]".format(e))



  


