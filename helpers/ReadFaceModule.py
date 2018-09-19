'''
Created on Dec 12, 2017

@author: Arun Bijapur
'''
import httplib, urllib, requests
from os.path import expanduser

from APICore import APICore
# import cognitive_face as CF  //commented by Sandeep Yadav as it is not being used 


APIRegion='eastus.api.cognitive.microsoft.com'
subScriptionKey1 = "e5062c708f5f4450aeaeb7220c9552e9"
subScriptionKey2 = "f5bc8efcc6e3413191caa1075c248077"


class ReadFaceModule():
    pass

    def invokeFaceAPI(self, apiMethod, apiUrl, body):
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
    
    def findSimilarFaces(self,faceId,faceListId, matchingMode):
        params = urllib.urlencode({
        })
        apiUrl="/face/v1.0/findsimilars?%s" % params
        
        body={    
            "faceId":faceId,
            "faceListId":faceListId,  
            "maxNumOfCandidatesReturned":10,
            "mode": matchingMode
        }
        responseData = self.invokeFaceAPI("POST", apiUrl, body)
        return responseData
        
    def listFaces(self,faceListId,):  
        
        params = urllib.urlencode({
        })
        apiUrl = "/face/v1.0/facelists/"+faceListId+"?%s" % params
           
        params = urllib.urlencode({
            # Request parameters
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,emotion',
        })
        body={
            
        }
        responseData = self.invokeFaceAPI("GET", apiUrl, body)
        return responseData
             
    def detectFace(self, faceImageUrl):
       
        
        params = urllib.urlencode({
            # Request parameters
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,emotion',
        })
        
        body={
            'url':faceImageUrl
            }
        
        apiUrl="/face/v1.0/detect?%s" % params
        return self.invokeFaceAPI("POST",apiUrl,body)
    
    def detectFaceByByteStream(self, image_64_encode):
       
        headers = {
            # Request headers
            'Content-Type': 'application/octet-stream',
            'ocp-apim-subscription-key': subScriptionKey1,
            'cache-control': "no-cache",
        }
        
        params = urllib.urlencode({
            # Request parameters
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,emotion,exposure',
        })
        
        body={
            image_64_encode
            }
        
        apiUrl="/face/v1.0/detect?%s" % params
         
       
        try:
            conn = httplib.HTTPSConnection(APIRegion)
            conn.request("POST", apiUrl, image_64_encode,headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
            return data
        except Exception as e:
            print("[Error no {0}] {1}".format(e.errno, e.strerror))
     
    def detectFaceByByteStreamCF(self, img):
       
       
        headers = {
            # Request headers
            'Content-Type': 'application/octet-stream',
            'ocp-apim-subscription-key': subScriptionKey1,
            'cache-control': "no-cache",
        }
        
        params = urllib.urlencode({
            # Request parameters
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,emotion',
        })
        
        body={
            bytes
            }
        
        apiUrl="https://"+APIRegion+"/face/v1.0/detect?%s" % params
        
        response = requests.post(apiUrl, data=img, headers=headers)
        #print(response.text)
        return response
             
    def identifyFace(self, faceId,personGroupId):
       
        
        params = urllib.urlencode({
        })
        
        body={    
        "personGroupId":personGroupId,
        "faceIds":[
            faceId
        ],
        "maxNumOfCandidatesReturned":2,
        "confidenceThreshold": 0.4
        }
        print("BEFORE APICORE CALL")

        apiUrl="/face/v1.0/identify?%s" % params
        apiMethod="POST"
        apiCore = APICore()
        return apiCore.invokeAPI(apiMethod,apiUrl,body)

