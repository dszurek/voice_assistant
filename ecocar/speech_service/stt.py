import pyaudio
import numpy as np
import whisper
import requests

stt = whisper.load_model("base.en")

class SpeechToTextService:
    def __init__(self, rate=16000, chunk_size=1024):
        self.rate = rate
        self.chunk_size = chunk_size
        self.model = whisper.load_model("base.en")
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1,
                                      rate=self.rate, input=True,
                                      frames_per_buffer=self.chunk_size)

    def transcribe(self):
        print("Listening...")
        frames = []
        while True:
            data = self.stream.read(self.chunk_size)
            frames.append(data)
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
            if len(audio_data) > self.rate * 5:  # Stop after 5 seconds of audio
                break

        print("Transcribing...")
        result = result = stt.transcribe(audio_data, fp16=True)
        return result["text"]


    def run(self):
        text = self.transcribe()
        print(f"Transcription: {text}")
        return text

if __name__ == "__main__":
    stt_service = SpeechToTextService()
    stt_service.run()