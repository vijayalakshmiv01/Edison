'''
Created on Dec 12, 2017

@author: Arun Bijapur
'''


import urllib

from APICore import APICore

class PersonGroupModule(object):
    
    def createPersonGroup(self):
        

        params = urllib.urlencode({
        })

        apiUrl="/face/v1.0/persongroups/1234?%s"
        apiMethod="PUT"
        body={
            "name":"naoBankBranchGroup",
            "userData":"nao:bank:branch"
        }
        apiCore = APICore()
        return apiCore.invokeAPI(apiMethod,apiUrl,body)
         
    def trainPersonGroup(self,personGroupId):
        

        params = urllib.urlencode({
        })
    
        apiUrl= "/face/v1.0/persongroups/"+personGroupId+"/train?%s"
        apiMethod="POST"
        body={
           
        }
        apiCore = APICore()
        return apiCore.invokeAPI(apiMethod,apiUrl,body)