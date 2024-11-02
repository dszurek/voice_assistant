import nltk
import torch
import warnings
import numpy as np
from transformers import AutoProcessor, BarkModel
import sounddevice as sd

class TextToSpeechService:
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.processor = AutoProcessor.from_pretrained("suno/bark-small")
        self.model = BarkModel.from_pretrained("suno/bark-small")
        self.model.to(self.device)
    
    def synthesize(self, text: str, voice_preset: str = "v2/en_speaker_6"):
        inputs = self.processor(text, voice_preset=voice_preset, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            audio_array = self.model.generate(**inputs, pad_token_id=10000)

        audio_array = audio_array.cpu().numpy().squeeze()
        sample_rate = self.model.generation_config.sample_rate
        return sample_rate, audio_array
    
    def play_audio(self, sample_rate: int, audio_array: np.ndarray):
        sd.play(audio_array, sample_rate)
        sd.wait()
    
if __name__ == "__main__":
    tts = TextToSpeechService()
    sample_text = "Hello, how are you?"
    sample_rate, audio_array = tts.synthesize(sample_text)
    tts.play_audio(sample_rate, audio_array)
    
