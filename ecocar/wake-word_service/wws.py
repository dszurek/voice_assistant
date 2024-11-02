import os.path
import logging
import types
from types import SimpleNamespace
import sys
import xml.etree.ElementTree as ET
import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model
import time
import threading
import pysine
from rich.console import Console

# # Add the parent directory (voice_assistant) to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# # Import the SpeechToTextService from the speech_service folder
from ecocar.speech_service.stt import SpeechToTextService

# Download pre-trained openwakeword models
openwakeword.utils.download_models()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)s %(message)s')

# Listener class declaration
class WakewordListener(threading.Thread):
    def __init__(self,
                 chunk_size=1280,
                 model_path="hey jarvis",
                 inference_framework='onnx',
                 channels=1,
                 rate=16000,
                 sleep_after_detection_in_seconds=4.0
                 ):
        super(WakewordListener, self).__init__()
        self._must_listen = False  # Flag to control listening state
        self._chunk_size = chunk_size  # Size of audio chunks to read from the microphone
        self._model_path = model_path  # Path to the wake word model
        self._inference_framework = inference_framework  # Inference framework to use (e.g., 'onnx')

        # Get microphone stream
        self._format = pyaudio.paInt16  # Audio format
        self._channels = channels  # Number of audio channels
        self._rate = rate  # Sampling rate
        self._sleep_after_detection_in_seconds = sleep_after_detection_in_seconds  # Sleep time after detection

        audio = pyaudio.PyAudio()  # Initialize PyAudio
        self._mic_stream = audio.open(format=self._format, channels=self._channels,
                                      rate=self._rate, input=True,
                                      frames_per_buffer=self._chunk_size)  # Open microphone stream

        # Load pre-trained openwakeword models
        if self._model_path != "":
            self._oww_model = Model(wakeword_models=[self._model_path],
                                    inference_framework=self._inference_framework)  # Load specified model
        else:
            self.oww_model = Model(inference_framework=self._inference_framework)  # Load default model

        self._n_models = len(self._oww_model.models.keys())  # Number of models loaded

    def start_stop(self):
        self._must_listen = not self._must_listen  # Toggle listening state
        logging.info(f"WakewordListener.start_stop(): self._must_listen = {self._must_listen}")

    def run(self):
        stt_service = SpeechToTextService()  # Initialize SpeechToTextService
        while True:
            if self._must_listen:
                wakeword_is_detected = False
                # Get audio
                audio = np.frombuffer(self._mic_stream.read(self._chunk_size), dtype=np.int16)  # Read audio chunk

                # Feed to openWakeWord model
                prediction = self._oww_model.predict(audio)  # Get prediction from model
                for wakeword, score in prediction.items():
                    if score > 0.5:  # Check if wake word is detected
                        logging.info(f"WakewordListener.run(): Wakeword detected! score = {score}")
                        wakeword_is_detected = True
                        self._oww_model.reset()  # Reset model state

                if wakeword_is_detected:
                    # Play sound to indicate wake word detection
                    self._play_detection_sound()
                    time.sleep(0.1)
                    chat_response = stt_service.run()
                    logging.info(f"Chatbot Response: {chat_response}")
                    # Sleep for a specified time after detection
                    time.sleep(self._sleep_after_detection_in_seconds)
            else:
                time.sleep(0.1)  # Increase sleep time to reduce CPU usage when not listening

    def _play_detection_sound(self):
        """Plays a sound to indicate wake word detection."""
        pysine.sine(440, 0.2)
        time.sleep(0.1)

def load_config(filepath="./wws-config.xml"):
    config = SimpleNamespace()
    tree = ET.parse(filepath)
    root_elm = tree.getroot()
    for root_child_elm in root_elm:
        if root_child_elm.tag == 'chunk_size':
            config.chunk_size = int(root_child_elm.text)
        elif root_child_elm.tag == 'model_wakeword':
            config.model_wakeword = root_child_elm.text
        elif root_child_elm.tag == 'inference_framework':
            config.inference_framework = root_child_elm.text
        elif root_child_elm.tag == 'channels':
            config.channels = int(root_child_elm.text)
        elif root_child_elm.tag == 'rate':
            config.rate = int(root_child_elm.text)
        elif root_child_elm.tag == 'sleep_after_detection_in_seconds':
            config.sleep_after_detection_in_seconds = float(root_child_elm.text)
        else:
            raise NotImplementedError(f"gui.load_config(): Not implemented element <{root_child_elm.tag}>")
    return config

config_filepath = "./wws-config.xml"
if not os.path.exists(config_filepath):
    raise FileNotFoundError(f"gui.py: Could not find filepath '{config_filepath}'. wws-config.xml file exist error.")

config = load_config(config_filepath)

global_params = SimpleNamespace()
global_params.is_running = False
global_params.wakerword_listener = WakewordListener(
    chunk_size=config.chunk_size,
    model_path=config.model_wakeword,
    inference_framework=config.inference_framework,
    channels=config.channels,
    rate=config.rate,
    sleep_after_detection_in_seconds=config.sleep_after_detection_in_seconds
)
global_params.wakerword_listener.daemon = True
global_params.wakerword_listener.start()

def start_stop():
    global global_params
    logging.info(f"start_stop() Initially: global_params.is_running = {global_params.is_running}")
    global_params.is_running = not global_params.is_running
    global_params.wakerword_listener.start_stop()
    logging.info(f"start_stop() Now: global_params.is_running = {global_params.is_running}")

if __name__ == "__main__":
    print("Press 's' to start/stop listening for the wake word, 'q' to quit.")
    while True:
        command = input().strip().lower()
        if command == 's':
            start_stop()
        elif command == 'q':
            break
        else:
            print("Invalid command. Press 's' to start/stop listening for the wake word, 'q' to quit.")
