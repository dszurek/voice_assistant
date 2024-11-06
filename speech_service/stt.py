import pyaudio
import numpy as np
import whisper
import requests
from queue import Queue
import time
import sounddevice as sd
from rich.console import Console
import threading
import os.path
import sys

 # Add the parent directory (voice_assistant) to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

 # Import the ChatService from the chat_service folder
from chat_service.chat import ChatService
from speech_service.tts import TextToSpeechService
from interaction_service.intService import InteractionService

class SpeechToTextService:
    def __init__(self, rate=16000, chunk_size=1024):
        self.console = Console()
        self.rate = rate
        self.chunk_size = chunk_size
        self.model = whisper.load_model("base.en")
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1,
                                      rate=self.rate, input=True,
                                      frames_per_buffer=self.chunk_size)
        self.chat_service = ChatService()
        self.tts_service = TextToSpeechService()
        self.i_service = InteractionService()
        
    def record_audio(self, stop_event, data_queue):
        silence_threshold = 500 #adjust based on environment, may need to be higher in car with road noise
        silence_duration = [0]
        silence_limit = 4 #seconds

        def callback(indata, frames, time, status):
            if status:
                self.console.print(status)
            data_queue.put(bytes(indata))

        # Check for silence
            audio_data = np.frombuffer(indata, dtype=np.int16)
            if np.abs(audio_data).mean() < silence_threshold:
                silence_duration[0] += frames / self.rate
            else:
                silence_duration[0] = 0

            # Set stop event if silence duration exceeds limit
            if silence_duration[0] >= silence_limit:
                stop_event.set()

        with sd.RawInputStream(
            samplerate=self.rate, dtype="int16", channels=1, callback=callback
        ):
            while not stop_event.is_set():
                time.sleep(0.1)

    def transcribe(self, audio_data: np.ndarray) -> str:
        with self.console.status("Transcribing...", spinner="dots4"):
            result = self.model.transcribe(audio_data, fp16=True)
            if isinstance(result, dict) and "text" in result and isinstance(result["text"], str):
                text = result["text"].strip()
            else:
                text = ""
        return text


    def run(self):
        data_queue = Queue()
        stop_event = threading.Event()
        recording_thread = threading.Thread(
            target=self.record_audio,
            args=(stop_event, data_queue),
        )
        recording_thread.start()

        recording_thread.join()

        audio_data = b"".join(list(data_queue.queue))
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        if audio_np.size > 0:
            self.console.status("Transcribing...", spinner="dots4")
            text = self.transcribe(audio_np)
            self.console.print(f"\nTranscription: {text}\n")

            #determine handling
            self.console.print("Checking for request...")
            if self.i_service.is_request(text):
                self.console.print("\n[green]Interaction Service Request[green]\n")
                response = self.i_service.handle_request(text)
            else:
                self.console.print("Chat Service Request")
                self.console.print("\n[blue]Sending to chatbot...[blue]\n")
                response = self.chat_service.get_response(text)
                self.console.print(f"Chatbot: {response}\n")
            
            self.i_service.varState()

            self.console.print("\nSynthesizing response...\n")
            self.tts_service.run(response)

            self.console.print("______________________________\n")

        else:
            self.console.print("[red]No audio data received.")

if __name__ == "__main__":
    stt_service = SpeechToTextService()
    stt_service.run()