import logging
from helpers.RunFaceModules import RunFaceModules
global moves_proxy
global awareness_proxy
global posture_proxy
global wait_for_user_trigger
global behavior_proxy
global photo_capture_proxy
global running_nao
global running_laptop
global running_laptop_nao
global device_name
global conversation_contd

run_face_modules = RunFaceModules()
class triggermanager(object):
    """
    A simple class to react to speech detection events.
    """

    def __init__(self, app,moves_prox,awareness_prox,posture_prox,photo_capture_prox,behavior_prox,wait_for_trigger,tmrunning_nao,tmrunning_laptop,tmrunning_laptop_nao,tmdevice_name,tmconversation_contd):
        """
        Initialisation of qi framework and event detection.
        """
        self.running_nao = tmrunning_nao
        self.running_laptop = tmrunning_laptop
        self.running_laptop_nao = tmrunning_laptop_nao
        self.device_name = tmdevice_name
        self.wait_for_user_trigger = wait_for_trigger
        self.moves_proxy = moves_prox
        self.awareness_proxy = awareness_prox
        self.posture_proxy = posture_prox
        self.photo_capture_proxy = photo_capture_prox
        self.behavior_proxy = behavior_prox
        self.conversation_contd = tmconversation_contd
        super(triggermanager, self).__init__()
        app.start()
        session = app.session
        vocabulary = ["Edison", "Roger", "Greetings","Stop"]
        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Connect the event callback.
        self.subscriber = self.memory.subscriber("WordRecognized")
        self.subscriber.signal.connect(self.on_word_recorgnized)
        # Get the services ALTextToSpeech and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        self.speech_recognition = session.service("ALSpeechRecognition")
        #self.speech_recognition.unsubscribe("triggermanager")
        self.speech_recognition.pause(False)
        self.speech_recognition.setLanguage("English")
        self.speech_recognition.setAudioExpression(False)
        self.speech_recognition.setVocabulary(vocabulary, False)
        self.speech_recognition.subscribe("triggermanager")
        self.first = True
        self.moves_proxy.setExpressiveListeningEnabled(False)
        self.awareness_proxy.stopAwareness()
        self.posture_proxy.goToPosture("Stand",0.5)
        print("posture_proxy")
        print(self.posture_proxy)
        print('end of triggermanager Constructor')
    
    def on_word_recorgnized(self, value):
        global behavior_proxy
        #global wait_for_user_trigger
        #global conversation_contd  
        global customer_name
        global trigger_command_file
        global offer_url
        global offer_data
        global offer_proxy
        logging.info('Word recognized:'+ str(value[0])+' confidence: '+str(value[1]))
        if not self.wait_for_user_trigger:
            print('entered')
            if 'Stop' in value[0] and  value[1] > 0.5:
                if(running_laptop_nao==device_name):
                    self.speech_recognition.unsubscribe("triggermanager")
            if 'Edison' in value[0] and  value[1] > 0.5:
                self.posture_proxy.goToPosture("Stand", 0.5)
                self.conversation_contd = True
                self.wait_for_user_trigger = True
                #triggerCommandFile = '/home/nao/branchdemo.wav'
                self.behavior_proxy.post.startBehavior('Stand/BodyTalk/Speaking/BodyTalk_20')
                #Get Next BEst Offer / Next Best Action from CDH
                #offer = requests.post(offerurl, data=offerdata, proxies=offerproxy)
                #if offer.status_code:
                #    logging.info(offer.json())
                print("value of wait_for_user_trigger", self.wait_for_user_trigger)
            elif 'Greetings' in value[0] and value[1] > 0.5:
                #                postureProxy.goToPosture("Stand", 0.5)
                self.behavior_proxy.post.startBehavior('Stand/BodyTalk/Speaking/BodyTalk_20')
                self.tts.say(" Please wait .. let me take a good look")
                self.photo_capture_proxy.setResolution(2)
                self.photo_capture_proxy.setPictureFormat("jpg")
                self.photo_capture_proxy.takePictures(1, "/home/nao/record/camera/", "image")
                customer_name = run_face_modules.detectAndIdentifyFace("/home/nao/record/camera/image.jpg")
                if customer_name != None:
                    logging.info('RECOGNIZED USER :' + customer_name)
                    self.tts.say(
                        'Welcome ' + customer_name + ' How can I help you? ')
                else:
                    self.tts.say(
                        'sorry I did not recognize you. Please do register ar myFedEx for a personalized experience')
            #    offer = requests.post(offerurl, data=offerdata, proxies=offerproxy)
            #    if offer.status_code:
            #        logging.info(offer.json())
            elif 'Roger' in value[0] and  value[1] > 0.5:
                self.posture_proxy.goToPosture("Stand", 0.5)
                #self.tts.say(" Please wait while I indentify ")
                #if self.first:
                #    triggerCommandFile='/home/nao/branchdemo.wav'
                #    self.first = False
                #else:
                #    photoCaptureProxy.setResolution(2)
                #    photoCaptureProxy.setPictureFormat("jpg")
                #    photoCaptureProxy.takePictures(1, "/home/nao/record/camera/", "image")
                #    customername = runFaceModules.detectAndIdentifyFace("/home/nao/record/camera/image.jpg")
                #    triggerCommandFile = '/home/nao/unrecog.wav'
                #    if customername != None:
                #        logging.info('RECOGNIZED USER :' + customername)
                #        if 'Jane' in customername:
                #           if 'Happy' in customername:
                #triggerCommandFile = '/home/nao/recog.wav'
                #            else:
                #                triggerCommandFile = '/home/nao/recogneutral.wav'
                #CONNV_CONT = True
                self.wait_for_user_trigger = True
                
                self.behavior_proxy.post.startBehavior('Stand/BodyTalk/Speaking/BodyTalk_20')
                print("end of word reco")