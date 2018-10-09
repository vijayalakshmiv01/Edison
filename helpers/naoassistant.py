from google.assistant.embedded.v1alpha1 import embedded_assistant_pb2, embedded_assistant_pb2_grpc
import grpc
import logging
import helpers.asshelp as assistant_helpers
import helpers.audhelp as audio_helpers
from google.rpc import code_pb2
import google.auth.transport.grpc
import google.auth.transport.requests
import requests
from tenacity import retry, stop_after_attempt, retry_if_exception

trigger_command_file = None

end_of_utterance = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE
dialog_follow_on = embedded_assistant_pb2.ConverseResult.DIALOG_FOLLOW_ON
close_microphone = embedded_assistant_pb2.ConverseResult.CLOSE_MICROPHONE

global running_nao
global running_laptop
global running_laptop_nao
global device_name
global conversation_contd
global wait_for_user_trigger
global behavior_proxy
global continue_conversation

class naoassistant(object):
    """Sample Assistant that supports follow-on conversations.
    Args:
      conversation_stream(ConversationStream): audio stream
        for recording query and playing back assistant answer.
      channel: authorized gRPC channel for connection to the
        Google Assistant API.
      deadline_sec: gRPC deadline in seconds for Google Assistant API call.
    """

    def swap_convo(self):
        if self.conversation_stream and self.conversation_stream._audio_type == 'wav':
            self.conversation_stream = self.conversation_stream_sd
            #self.conversation_stream_wav.restart_wav()
        else:
            self.conversation_stream = self.conversation_stream_wav
            self.conversation_stream.restart_wav()

    def __init__(self, conversation_stream, channel, deadline_sec, conversation_stream_wav,nsrunning_nao,nsrunning_laptop,nsrunning_laptop_nao,nsdevice_name,nsconversation_contd, nsbehavior_proxy):
        print("enetered into contructor of assistant")
        self.running_nao = nsrunning_nao
        self.running_laptop = nsrunning_laptop
        self.running_laptop_nao = nsrunning_laptop_nao
        self.device_name = nsdevice_name
        self.conversation_contd = nsconversation_contd
        
        self.behavior_proxy = nsbehavior_proxy
        
        self.conversation_stream = None
        #self.conversation_stream = conversation_stream
        self.conversation_stream_sd = conversation_stream
        self.conversation_stream_wav = conversation_stream_wav
        self.conversation_state = None
        
        # Create Google Assistant API gRPC client.
        # Running from laptop or laptop connected with nao uses pb2_grpc.EmbeddedAssistantStub
        #Running in nao uses pb2.EmbeddedAssistantStub.
        if(self.running_laptop==self.device_name or self.running_laptop_nao==self.device_name):
            self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(channel)
        else:
            self.assistant = embedded_assistant_pb2.EmbeddedAssistantStub(channel)
            #self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(channel)
        
        self.deadline = deadline_sec
        print("end of the assisant")

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False
        self.conversation_stream.close()

    def is_grpc_error_unavailable(e):
        is_grpc_error = isinstance(e, grpc.RpcError)
        if is_grpc_error and (e.code() == grpc.StatusCode.UNAVAILABLE):
            logging.error('grpc unavailable error: %s', e)
            return True
        return False

    @retry(reraise=True, stop=stop_after_attempt(3),
           retry=retry_if_exception(is_grpc_error_unavailable))
    def converse(self,nsrunning_nao,nsrunning_laptop,nsrunning_laptop_nao,nsdevice_name):
        """Send a voice request to the Assistant and playback the response.
        Returns: True if conversation should continue.
        """
        print("entered into naoassistant converse")
        self.conversation_contd = True
        global trigger_command_file
        
        #global conn

        #global bhvr
        # SETS INITIAL STREAM, the wav one
        if self.conversation_stream == None and self.conversation_stream_wav:
            self.conversation_stream = self.conversation_stream_wav
        
        elif self.conversation_stream == None:
            self.conversation_stream = self.conversation_stream_sd

        # KEEPS out.wav blank, comment out if you need it
        if self.conversation_stream._audio_out == 'wav':
            self.conversation_stream.restart_wav_out()

        # change when trigger command is given
        if (trigger_command_file != None):
            self.conversation_stream = audio_helpers.ConversationStream(
                source=audio_helpers.WaveSource(open(trigger_command_file, 'rb'),sample_rate=audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE,sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH),
                sink= audio_helpers.SoundDeviceStream(sample_rate=audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE,sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,block_size=audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,flush_size=audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE),
                iter_size=audio_helpers.DEFAULT_AUDIO_ITER_SIZE,
                sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
                audio_type='wav',
                audio_out='sd')
            trigger_command_file = None
        else:
            self.conversation_stream = self.conversation_stream_sd

        self.continue_conversation = False

        self.conversation_stream.start_recording()
        if trigger_command_file != None:
            trigger_command_file = None
            self.conversation_stream.stop_recording()
        logging.info('Recording audio request.')
      
        def iter_converse_requests():
            for c in self.gen_converse_requests():
                assistant_helpers.log_converse_request_without_audio(c)
                yield c
            self.conversation_stream.start_playback()

        # This generator yields ConverseResponse proto messages
        # received from the gRPC Google Assistant API.
        for resp in self.assistant.Converse(iter_converse_requests(),
                                            self.deadline):

            assistant_helpers.log_converse_response_without_audio(resp)
            if resp.error.code != code_pb2.OK:
                logging.error('server error: %s', resp.error.message)
                break

            if resp.event_type == end_of_utterance:
                logging.info('End of audio request detected')
                self.conversation_stream.stop_recording()

                #if self.conversation_stream._audio_type == 'wav':
                #    self.conversation_stream.restart_wav()
                #print("\nin end of utterance\n")

            if resp.result.spoken_request_text:
                logging.info('Transcript of user request: "%s".',
                             resp.result.spoken_request_text)
                logging.info('self.device_name'+self.device_name)             
                if(self.running_nao==self.device_name or self.running_laptop_nao==self.device_name):

                    logging.info("entered to find the keyword")
                    if 'introduce' in resp.result.spoken_request_text:
                    #    if CONNV_CONT:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Emotions/Neutral/Hello_1')
                    #   else:
                    #       bhvrProxy.post.startBehavior('animations/Stand/Gestures/Garlic_city')
                    elif 'awards' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Emotions/Positive/Ecstatic_1')
                        #bhvrProxy.post.startBehavior('animations/Stand/Gestures/Me_7')
                    elif 'history' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Gestures/Mime_1')
                    elif 'sparkle' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Emotions/Positive/Ecstatic_1')
                        #bhvrProxy.post.startBehavior('animations/Stand/Gestures/Me_3')
                    elif 'ramp-up' in resp.result.spoken_request_text or 'ramp up' in resp.result.spoken_request_text:
                        #bhvrProxy.post.startBehavior('animations/Stand/Gestures/Applause_1')
                        self.behavior_proxy.post.startBehavior('animations/Stand/Gestures/Salute_2')
                    elif 'talent' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Emotions/Negative/Disappointed_1')
                        #bhvrProxy.post.startBehavior('animations/Stand/Gestures/Me_7')
                    elif 'picture' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Gestures/Joy_1')
                        #bhvrProxy.post.startBehavior('animations/Stand/Gestures/BowShort_1')
                    elif 'congrats' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Emotions/Positive/Winner_2')
                    elif 'lost' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Emotions/Negative/Disappointed_1')
                    elif 'closing' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Gestures/Salute_1')
                    elif 'Jane' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('animations/Stand/Gestures/Give_1')
                    elif 'forward' in resp.result.spoken_request_text:
                        logging.info("Before moving forward")
                        self.behavior_proxy.post.startBehavior('motions/move_forward')
                    elif 'backward' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('motions/move_backward')
                    elif 'right' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('motions/move_right')
                    elif 'left' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('motions/move_left')
                    elif 'sit' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('motions/sitDown')
                    elif 'stand' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('motions/standUp')
                    elif 'photo' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('motions/take_photo')
                    elif 'dance' in resp.result.spoken_request_text:
                        self.behavior_proxy.post.startBehavior('gangnamstyle/GangnamStyle')                  
                    logging.info("***********************************************")    
                        #bhvrProxy.post.startBehavior('animations/Stand/Waiting/LookHand_2')
                logging.info('Playing assistant response.')


            # "Writes" audio to speaker/stream or wav file
            if len(resp.audio_out.audio_data) > 0:
                self.conversation_stream.write(resp.audio_out.audio_data)
                if(self.conversation_contd and self.running_nao==self.device_name or self.running_laptop_nao==self.device_name):
                    self.behavior_proxy.post.startBehavior('Stand/BodyTalk/Speaking/BodyTalk_10')
            if resp.result.spoken_response_text:
                logging.info(
                    'Transcript of TTS response '
                    '(only populated from IFTTT): "%s".',
                    resp.result.spoken_response_text)

            #bhvrProxy.stopBehavior('Stand/BodyTalk/Speaking/BodyTalk_10')

            if resp.result.conversation_state:
                self.conversation_state = resp.result.conversation_state

            if resp.result.volume_percentage != 0:
                self.conversation_stream.volume_percentage = (
                    resp.result.volume_percentage
                )

            if resp.result.microphone_mode == dialog_follow_on:
                self.continue_conversation = self.conversation_contd
                print("value stop of microphone", self.conversation_contd)
                logging.info('Expecting follow-on query from user.')

            elif resp.result.microphone_mode == close_microphone:
                self.continue_conversation = False
                logging.info('Finished conversation.')

        logging.info('Finished playing assistant response.')
        self.conversation_stream.stop_playback()
        


        if not self.continue_conversation and self.conversation_stream_wav:
            self.conversation_stream = self.conversation_stream_wav
            self.conversation_stream.restart_wav()

        return self.continue_conversation

    def gen_converse_requests(self):
        """Yields: ConverseRequest messages to send to the API."""

        converse_state = None
        if self.conversation_state:
            logging.debug('Sending converse_state: %s',
                          self.conversation_state)
            converse_state = embedded_assistant_pb2.ConverseState(
                conversation_state=self.conversation_state,
            )
        config = embedded_assistant_pb2.ConverseConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
                volume_percentage=self.conversation_stream.volume_percentage,
            ),
            converse_state=converse_state
        )
        # The first ConverseRequest must contain the ConverseConfig
        # and no audio data.
        yield embedded_assistant_pb2.ConverseRequest(config=config)
        for data in self.conversation_stream:
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.ConverseRequest(audio_in=data)
