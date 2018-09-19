from collections import namedtuple
import json, base64
from os import environ
from os.path import expanduser

from FaceModule import FaceModule
from PersonGroupModule import PersonGroupModule
from PersonModule import PersonModule
from ReadFaceModule import ReadFaceModule


orgFaceImageUrl="https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg"
elvisPresleyImage="https://www.thesun.co.uk/wp-content/uploads/2016/11/nintchdbpict000256253516.jpg?w=637&strip=all"
steveImage="http://all4desktop.com/data_images/original/4173835-steve-jobs.jpg"
arunsImage="https://lh3.googleusercontent.com/-Kgur8nJvA0o/ThB62YjmJkI/AAAAAAAAEHw/2wfjS79nV3c/w530-h529-n/MyPhoto1.jpg"
raghusImage="https://pbs.twimg.com/profile_images/437826080968175616/zMzVw0wK_400x400.jpeg"

newPersonas = [{'name':'Arun Bijapur','dept':'Cognitive Technologies','role':'Architect','photoImage':'https://lh3.googleusercontent.com/-Kgur8nJvA0o/ThB62YjmJkI/AAAAAAAAEHw/2wfjS79nV3c/w530-h529-n/MyPhoto1.jpg'},{'name':'Raghu ML','dept':'Customer Analytics and Digital','role':'Vice President','photoImage':'https://pbs.twimg.com/profile_images/437826080968175616/zMzVw0wK_400x400.jpeg'}]
personGroupId="12345"
faceImageUrl=steveImage
enableCloudAPIResponseLog = True
enableMethodLogging = True

class RunFaceModules(object):
    NORMAL_LOGGIN = "NL"
    CLOUD_API_RESP_LOG = "CARL"
    pass
    
    def log(self,logMessage,loggingType):
        if(loggingType == self.CLOUD_API_RESP_LOG and enableCloudAPIResponseLog):
            print(logMessage)
        if(loggingType == self.NORMAL_LOGGIN and enableMethodLogging):
            print(logMessage)
            
    def _byteify(self,data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
        if isinstance(data, unicode):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [ self._byteify(item, ignore_dicts=True) for item in data ]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return {
                self._byteify(key, ignore_dicts=True): self._byteify(value, ignore_dicts=True)
                for key, value in data.iteritems()
            }
        # if it's anything else, return it in its original form
        return data
    def getObjectFromJson(self,jsonData):
        #object= json.loads(jsonData,object_hook=_byteify)
        object =  json.loads(jsonData, object_hook=lambda  d: namedtuple('jsonObj', d.keys())(*d.values()))
        return object
    def detectAndIdentifyFace(self, imagePath):
        
        self.log("Detecting Face on Cloud with AI Cognitive API",RunFaceModules.NORMAL_LOGGIN)
        faceModule = FaceModule()
        #faceModule.createFaceList()
        #faceModule.addFaceToFaceList()
        
        readFaceModule = ReadFaceModule()
        #response=readFaceModule.detectFace(faceImageUrl)
        
        #data =  open('C:\Arun\steve.jpg', 'rb').read()
        
        #image = open('C:\Arun\steve.jpg', 'rb') #open binary file in read mode
        #image = open('C:\Arun\elvis.jpg', 'rb')
        #image = open('C:\Arun\uk_celeb.jpg', 'rb')
        image = open(imagePath, 'rb')
        image_read = image.read()
       ## image_64_encode = base64.encodestring(image_read)
        image.close()
        
       

        #data =  open('C:\Arun\Steve_Jobs.PNG', 'rb').read()
       ## print('-------------------------')
        #print(image_64_encode)
       # print('-------------------------')
        #response=readFaceModule.detectFaceByByteStream(image_64_encode)
        
        response=readFaceModule.detectFaceByByteStream(image_read)
        self.log("response data is "+str(response),RunFaceModules.NORMAL_LOGGIN)
        responseJson = response
        #print('--------------Detect Face Response---------')
        #print(responseJson)
        #print('---------End of Detect Face Response -------')
        jsonObj = self.getObjectFromJson(responseJson)
        faceIdToMatch=""
        if(len(jsonObj)>0):
            #faceIdToMatch=str(jsonObj[0].faceId)
            faceIdToMatch=self.getBestExposedFaceId(jsonObj)
            isPersonHappy = self.isHappy(jsonObj)
            match = self.identifyAndWishPerson(faceIdToMatch)
            if isPersonHappy:
                return "Happy " + match
            else:
                return "Neutral " + match
        else:
            self.log("Sorry can't detect face in supplied picture",RunFaceModules.NORMAL_LOGGIN)
        print(faceIdToMatch)
        
        #readFaceModule.listFaces("1234567")
        #readFaceModule.findSimilarFaces("926a7791-dc71-4225-9991-f726daae34a3", "1234", "matchFace")


        
        
       
    def getBestExposedFaceId(self,jsonObject):
        bestExposedLevel = 0;
        bestExposedFaceId =""
        for faceJson in jsonObject:
            if(faceJson.faceAttributes.exposure.value>bestExposedLevel):
                bestExposedFaceId = str(faceJson.faceId)
        self.log("Found best exposed face id:"+bestExposedFaceId,RunFaceModules.NORMAL_LOGGIN)
        return bestExposedFaceId
    
    def isHappy(self,jsonObject):
        happy = False
        for emoJson in jsonObject:
            if(emoJson.faceAttributes.emotion.happiness>0.2):
                happy = True
        self.log("Emotion recognized as happy :"+str(happy),RunFaceModules.NORMAL_LOGGIN)
        return happy


    def createAndlearnPesonFaces(self):
        #Person Group
        personGroupModule = PersonGroupModule()
        #personGroupModule.createPersonGroup()
        #personGroupModule.trainPersonGroup(personGroupId)
        #Person
        personModule = PersonModule()
        #personaArray = json.load(newPersonas);
        for newPersona in newPersonas:
            self.log("Uploading Persona:"+newPersona['name']+" to cloud store",RunFaceModules.NORMAL_LOGGIN)
            response=personModule.createPerson(personGroupId,newPersona['name'],"age:25;height:5.9")
            responseJson = json.loads(response,object_hook=self._byteify)
            if(len(responseJson)>0):
                response = personModule.addFaceToPerson(responseJson["personId"],newPersona['photoImage'],"emotion:smile",personGroupId)
            self.log("Upload completed",RunFaceModules.NORMAL_LOGGIN)
            #print (detectedPersonResponse)
        #Learn Elvis Face
        #responseJson = json.loads(response,object_hook=self._byteify)
        #if(len(responseJson)>0):
        #    response = personModule.addFaceToPerson(responseJson["personId"],elvisPresleyImage,"emotion:smile",personGroupId)
        #  print(response)
    
        #Learn Elvis Face
        #response=personModule.createPerson(personGroupId,"Steve Jobs","age:25;height:5.9")
        #responseJson = json.loads(response,object_hook=self._byteify)
        #if(len(responseJson)>0):
        #    response = personModule.addFaceToPerson(responseJson["personId"],steveImage,"emotion:smile",personGroupId)
        # print(response)
        print ("Training Cognitive Engine....")
        personGroupModule.trainPersonGroup(personGroupId)
        print ("Training Completed....")

#Learn Steve Face
#personModule.createPerson("1234","Steve Jobs","age:40;height:6.1")

#personModule.addFaceToPerson("99b2c58e-ebf3-403d-aabc-67f5d30e52a5",steveImage,"emotion:smile",personGroupId)


    
    def identifyAndWishPerson(self,faceIdToMatch):
        readFaceModule = ReadFaceModule()
        personGroupModule = PersonGroupModule()
        #print(faceIdToMatch)
        #faceIdToMatch=steveFaceId
        personId =""
        response = readFaceModule.identifyFace(faceIdToMatch, personGroupId)
        self.log("Identify Face API Resp:"+response,RunFaceModules.NORMAL_LOGGIN)
        responseJson = json.loads(response,object_hook=self._byteify)
        #print('---------Identify Face Response--------')
        #print(responseJson)
        #print('---------End of Identify Face Response--------')
        if(len(responseJson)>0):
            matchedCandidates=responseJson[0].get('candidates')
            if(len(matchedCandidates)>0):
                personId = matchedCandidates[0].get('personId')
                #print ("Res in test:"+responseJson)        
                personModule = PersonModule()
                response = personModule.getPerson(personId,personGroupId)
                responseJson = json.loads(response,object_hook=self._byteify)
                #print('---------Get person Response--------')
                #print(responseJson)
                #print('---------End of Get person Response--------')
                personName = responseJson.get('name')
                #print("Hi "+personName+", welcome to the branch, How are you doing today!!!")
                return personName
            else:
                #print("Hello, I am not sure if we have met already, My name is Robo. How may I help you")
                return "Unknown"
        else:
            print("Unknown Error, please check response")       
