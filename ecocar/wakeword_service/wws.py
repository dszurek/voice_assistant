import os.path
import logging
import sys
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


class WakeWordService:
    def __init__(self):
        self.console = Console()
        self.is_running = False
        self.wwl = WakewordListener()
        self.wwl.daemon = True
    
    def start(self):
        self.wwl.start()
        self.is_running = True
        self.wwl.start_stop()
    
    def stop(self):
        self.wwl.start_stop()
        self.is_running = False
        
# Listener class declaration
class WakewordListener(threading.Thread):
    def __init__(self,
                 chunk_size=1280,
                 model_path="hey jarvis",
                 inference_framework='onnx',
                 channels=1,
                 rate=16000,
                 sleep_seconds=2.0
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
        self._sleep_seconds = sleep_seconds  # Sleep time after detection

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
                    time.sleep(self._sleep_seconds)
            else:
                time.sleep(0.1)  # Increase sleep time to reduce CPU usage when not listening

    def _play_detection_sound(self):
        """Plays a sound to indicate wake word detection."""
        pysine.sine(440, 0.2)
        time.sleep(0.1)


if __name__ == "__main__":
    wakeword_service = WakeWordService()
    wakeword_service.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        wakeword_service.stop()
        logging.info("Exiting WakeWordService...")