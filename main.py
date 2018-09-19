"""Sample that implements gRPC client for Google Assistant API."""
import json
import logging
import os.path
import requests
import grpc
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from PIL import Image
from google.assistant.embedded.v1alpha1 import embedded_assistant_pb2, embedded_assistant_pb2_grpc
from google.rpc import code_pb2
from tenacity import retry, stop_after_attempt, retry_if_exception

#Helper Files
import helpers.asshelp as assistant_helpers
import helpers.audhelp as audio_helpers
from helpers.RunFaceModules import RunFaceModules
from helpers.PersonGroupModule import PersonGroupModule
from helpers.naoassistant import naoassistant
from helpers.triggermanager import triggermanager
import time
import sys
import sounddevice as sd

# nao,to run on Edison
# laptop, to run assistant independently on laptop
# laptop_nao, to connect to nao from laptop.
running_nao = "nao"
running_laptop = 'laptop'
running_laptop_nao = 'laptop_nao'
device_name = 'nao'
if(running_nao==device_name or running_laptop_nao==device_name):
    try:
        import qi
    except:
        print('Module qi not installed')
    try:
        from naoqi import ALProxy
    except:
        print('Module naoqi not installed')


#Assistant Constant Variables
assistant_api_endpoint = 'embeddedassistant.googleapis.com'
port = 9559
behavior_proxy = None
nao_ip_address = '192.168.1.102'
if(running_laptop==device_name):
    print('No need proxy of nao module as Running on laptop')
    ip = nao_ip_address
else:
    #GLOBAL VARIABLES
    if(running_laptop_nao==device_name):
        ip = nao_ip_address
    else:
        ip = '127.0.0.1'
    face_size = 3.0
    offer_url = 'https://mphasis01.pegalabs.io/prweb/PRRestService/PegaMKTContainer/V2/Container'
    offer_data = '{"CustomerID":"C00001","ContainerName":"SalesOffers"}'
    offer_proxy = {'http': 'http://5i1doj4tup4vlb:UEV-_l--1hZATTC6IzVn7KPEyQ@us-east-static-01.quotaguard.com:9293',
                'https': 'http://5i1doj4tup4vlb:UEV-_l--1hZATTC6IzVn7KPEyQ@us-east-static-01.quotaguard.com:9293'}
    behavior_proxy = ALProxy("ALBehaviorManager", ip,port)
    moves_proxy = ALProxy("ALAutonomousMoves",ip,port)
    awareness_proxy = ALProxy("ALBasicAwareness",ip,port)
    photo_capture_proxy = ALProxy("ALPhotoCapture", ip,port)
    dialog_proxy = ALProxy("ALDialog", ip,port)
    posture_proxy = ALProxy("ALRobotPosture",ip,port)
if(running_laptop==device_name):
    wait_for_user_trigger = True
    conversation_contd = True
else:
    wait_for_user_trigger = False
    conversation_contd = False
motion = None
customer_name = None
trigger_command_file = None
global user_triggered
tracker = None
#Main method
def main():
    api_endpoint = assistant_api_endpoint
    log_path_name = None
    verbose = False
    input_audio_file = None
    output_audio_file = None
    audio_sample_rate = 16000
    audio_sample_width = 2
    audio_iter_size = 3200
    audio_block_size = 6400
    audio_flush_size = 25600
    grpc_deadline = 185
    nao_ip = '127.0.0.1'
    
    if(running_laptop==device_name or running_laptop_nao==device_name):
        credentials = "C:/Backup/GoogleAssistantNao/edison/credentials.json"
        log_path_name = "C:/Backup/GoogleAssistantNao/edison/logs"
        
    else:
        credentials = "/home/nao/GoogleAssistantNao/edison/credentials.json"  
        log_path_name = "/home/nao/GoogleAssistantNao/edison/logs" 
    logging.basicConfig(filename= log_path_name,level=logging.DEBUG if verbose else logging.INFO)

    logging.info('=======================================')
    logging.info('api_endpoint:: '+api_endpoint)
    logging.info('credentials: '+credentials)
    logging.info('verbose: '+str(verbose))
    logging.info('input_audio_file: '+ str(input_audio_file))
    logging.info('output_audio_file: '+ str(output_audio_file))
    logging.info('=======================================')
    logging.info('audio_sample_rate: ')
    logging.info(audio_sample_rate)
    logging.info('=======================================')
    logging.info('audio_sample_width: ')
    logging.info(audio_sample_width)
    logging.info('=======================================')
    logging.info('audio_iter_size: ')
    logging.info(audio_iter_size)
    logging.info('=======================================')
    logging.info('audio_block_size:')
    logging.info(audio_block_size)
    logging.info('=======================================')
    logging.info('audio_flush_size:')
    logging.info(audio_flush_size)
    logging.info('=======================================')
    logging.info('grpc_deadline:')
    logging.info(grpc_deadline)
    logging.info('=======================================')
    
    #GLOBAL VARS
    global wait_for_user_trigger
    global motion
    global behavior_proxy
    global tracker
    global conversation_contd
    
    # Load OAuth 2.0 credentials.
    try:
        with open(credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None, **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        return

    # Create an authorized gRPC channel.
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, api_endpoint)
    logging.info('Connecting to %s', api_endpoint)
    logging.info('Connecting to %s', api_endpoint)

    # Configure audio source and sink for sounddevice.
    audio_device = None
    audio_source = audio_device = (
        audio_device or audio_helpers.SoundDeviceStream(
            sample_rate=audio_sample_rate,
            sample_width=audio_sample_width,
            block_size=audio_block_size,
            flush_size=audio_flush_size
        )
    )
    audio_sink = audio_device = (
        audio_device or audio_helpers.SoundDeviceStream(
            sample_rate=audio_sample_rate,
            sample_width=audio_sample_width,
            block_size=audio_block_size,
            flush_size=audio_flush_size
        )
    )

    # Create conversation stream with the given audio source and sink.
    conversation_stream = audio_helpers.ConversationStream(
        source=audio_source,
        sink=audio_sink,
        iter_size=audio_iter_size,
        sample_width=audio_sample_width,
        audio_type='sd',
        audio_out='sd'
    )

    conversation_stream_wav = None
    if(running_laptop==device_name):
        logging.info('Calling Nao Assistant Class')
        try:
            with naoassistant(conversation_stream, grpc_channel, grpc_deadline, conversation_stream_wav,running_nao,running_laptop,running_laptop_nao,device_name,conversation_contd, behavior_proxy) as assistant:
                while True:
                    continue_conversation = assistant.converse(running_nao,running_laptop,running_laptop_nao,device_name)
                    # wait for user trigger if there is no follow-up turn in
                    # the conversation.
                    wait_for_user_trigger = continue_conversation
        except KeyboardInterrupt:
                logging.debug('Program Ending Keyboard Interupt')
                sys.exit(0)                

    else:
        if nao_ip:
            # voice detection
            nao_ip = ip
            nao_ip = str(nao_ip)
            nao_port = port
            wait_for_user_trigger = False
            motion = ALProxy("ALMotion", nao_ip, nao_port)
            #tracker = ALProxy("ALTracker", nao_ip, nao_port)

            try:
                # Initialize qi framework.
                connection_url = "tcp://" + nao_ip + ":" + str(nao_port)
                app = qi.Application(["triggermanager", "--qi-url=" + connection_url])
            except RuntimeError:
                logging.info ("Can't connect to Naoqi at ip \"" + nao_ip + "\" on port " + str(nao_port) +".\n"
                    "Please check your script arguments. Run with -h option for help.")
                sys.exit(1)
            trigger_manager = triggermanager(app,moves_proxy,awareness_proxy,posture_proxy,photo_capture_proxy,behavior_proxy,wait_for_user_trigger,running_nao,running_laptop,running_laptop_nao,device_name,conversation_contd)
            logging.info("Before calling the naoassistant")
            global conversation_contd 
            try:
                with naoassistant(conversation_stream,grpc_channel, grpc_deadline, conversation_stream_wav,running_nao,running_laptop,running_laptop_nao,device_name,conversation_contd,behavior_proxy) as assistant:
                    logging.info("Value of wait_for_user_trigger after assistant invoked:")
                    logging.info(wait_for_user_trigger)
                    conversation_contd = assistant.conversation_contd
                    while True:
                        # if not wait_for_user_trigger:
                        #     click.pause(info='Press Enter to send a new request...')
                        if not wait_for_user_trigger:
                            logging.info('Waiting For command...')
                        while not wait_for_user_trigger:
                            time.sleep(1)
                            wait_for_user_trigger = trigger_manager.wait_for_user_trigger
                        continue_conversation = assistant.converse(running_nao,running_laptop,running_laptop_nao,device_name)
                        # wait for user trigger if there is no follow-up turn in
                        # the conversation.
                        logging.info("Value of continue_conversation:")
                        logging.info(continue_conversation)
                        wait_for_user_trigger = continue_conversation
                        trigger_manager.wait_for_user_trigger = continue_conversation
                        trigger_manager.conversation_contd = continue_conversation
            except KeyboardInterrupt:
                logging.info('Program Ending, Unsubscribing Speech recognition')
                trigger_manager.speech_recognition.unsubscribe("triggermanager")
                motion.rest()
                sys.exit(0)

if __name__ == '__main__':
    main()
