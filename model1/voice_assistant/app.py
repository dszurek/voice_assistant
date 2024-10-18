import time
import threading
import numpy as np
import logging
import whisper
import sounddevice as sd
from queue import Queue
from rich.console import Console
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from ttss import TextToSpeechService
import nltk
nltk.download("punkt")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set logging level to WARNING, delete these when trying to see subprocesses execute. Could be useful to see what's taking the longest
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

console = Console()
stt = whisper.load_model("base.en")
tts = TextToSpeechService()

template = """
You are a helpful assistant for the EcoCAR Lyriq car. You are polite, respectful, and aim to provide concise responses of less 
than 20 words. You can make calls, set navigation destinations, and turn on various functionalities of the car.
You occasionally end responses with 'ROLL TIDE!', but never more than once per every five responses.
The conversation transcript is as follows:
{history}
And here is the user's follow-up: {input}
Your response:
"""
PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
chain = ConversationChain(
    prompt=PROMPT,
    verbose=False,
    memory=ConversationBufferMemory(ai_prefix="Assistant:"),
    llm=OllamaLLM(model="llama3.2:1b ")
)

def record_audio(stop_event, data_queue):
    """
    Captures audio data from the user's microphone and adds it to a queue for further processing.
    Args:
        stop_event (threading.Event): An event that, when set, signals the function to stop recording.
        data_queue (queue.Queue): A queue to which the recorded audio data will be added.
    Returns:
        None
    """
    def callback(indata, frames, time, status):
        if status:
            console.print(status)
        data_queue.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=16000, dtype="int16", channels=1, callback=callback
    ):
        while not stop_event.is_set():
            time.sleep(0.1)

def transcribe(audio_np: np.ndarray) -> str:
    """
    Transcribes the given audio data using the Whisper speech recognition model.
    Args:
        audio_np (numpy.ndarray): The audio data to be transcribed.
    Returns:
        str: The transcribed text.
    """
    result = stt.transcribe(audio_np, fp16=True)  # Set fp16=True if using a GPU
    
    # Log the type and content of result
    logging.debug(f"Type of result: {type(result)}")
    logging.debug(f"Content of result: {result}")
    
    if isinstance(result, dict) and "text" in result and isinstance(result["text"], str):
        text = result["text"].strip()
    else:
        logging.error("Unexpected result format or missing 'text' key")
        text = ""
    
    return text

def get_llm_response(text: str) -> str:
    """
    Generates a response to the given text using the Llama-3.2 language model.
    Args:
        text (str): The input text to be processed.
    Returns:
        str: The generated response.
    """
    response = chain.predict(input=text)
    if response.startswith("Assistant:"):
        response = response[len("Assistant:") :].strip()
    return response

def play_audio(sample_rate, audio_array):
    """
    Plays the given audio data using the sounddevice library.
    Args:
        sample_rate (int): The sample rate of the audio data.
        audio_array (numpy.ndarray): The audio data to be played.
    Returns:
        None
    """
    sd.play(audio_array, sample_rate)
    sd.wait()
if __name__ == "__main__":
    console.print("[cyan]Assistant started! Press Ctrl+C to exit.")

    try:
        while True:
            console.input(
                "Press Enter to start recording, then press Enter again to stop."
            )

            data_queue = Queue()  # type: ignore[var-annotated]
            stop_event = threading.Event()
            recording_thread = threading.Thread(
                target=record_audio,
                args=(stop_event, data_queue),
            )
            recording_thread.start()

            input()
            stop_event.set()
            recording_thread.join()

            audio_data = b"".join(list(data_queue.queue))
            audio_np = (
                np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            )

            if audio_np.size > 0:
                with console.status("Transcribing...", spinner="earth"):
                    text = transcribe(audio_np)
                console.print(f"[yellow]You: {text}")

                with console.status("Generating response...", spinner="earth"):
                    response = get_llm_response(text)
                    sample_rate, audio_array = tts.long_form_synthesize(response)

                console.print(f"[cyan]Assistant: {response}")
                play_audio(sample_rate, audio_array)
            else:
                console.print(
                    "[red]No audio recorded. Please ensure your microphone is working."
                )

    except KeyboardInterrupt:
        console.print("\n[red]Exiting...")

    console.print("[blue]Session ended.")