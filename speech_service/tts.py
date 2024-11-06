import nltk
import torch
import warnings
import numpy as np
from transformers import AutoProcessor, BarkModel
import sounddevice as sd
import pyttsx3

class TextToSpeechService:
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.processor = AutoProcessor.from_pretrained("suno/bark-small")
        self.model = BarkModel.from_pretrained("suno/bark-small")
        self.model.to(self.device)
        self.engine = pyttsx3.init()

    def play_audio(self, text, engine, voice):

        engine.setProperty('voice', voice)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()

    def run(self, text: str):
        self.play_audio(text, self.engine, "david")


if __name__ == "__main__":
    tts = TextToSpeechService()
    sample_text = "Hello, how are you?"
    tts.run(sample_text)
    
