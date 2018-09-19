'''
Created on Dec 12, 2017

@author: Arun Bijapur
'''

import  urllib

from APICore import APICore


class PersonModule(object):
    pass

    def createPerson(self,personGroupId, personName,personUserData,):
        params = urllib.urlencode({
        })

        apiUrl="/face/v1.0/persongroups/"+personGroupId+"/persons?%s" % params
        apiMethod="POST"
        body={
            "name":personName,
            "userData":personUserData
        }
        apiCore = APICore()
        return apiCore.invokeAPI(apiMethod,apiUrl,body)
    
    def addFaceToPerson(self,personId, personFaceUrl,faceUserData,personGroupId):
        params = urllib.urlencode({
        # Request parameters
        'userData': faceUserData,
        'targetFace': '',
        })

        apiUrl="/face/v1.0/persongroups/"+personGroupId+"/persons/"+personId+"/persistedFaces?%s" % params
        apiMethod="POST"
        body={
            "url":personFaceUrl
        }
        apiCore = APICore()
        return apiCore.invokeAPI(apiMethod,apiUrl,body)
    
    def getPerson(self,personId,personGroupId):
        params = urllib.urlencode({
        })

        apiUrl="/face/v1.0/persongroups/"+personGroupId+"/persons/"+personId+"?%s" % params
        apiMethod="GET"
        body={
            
        }
        apiCore = APICore()
        return apiCore.invokeAPI(apiMethod,apiUrl,body)
            
    
            
            
