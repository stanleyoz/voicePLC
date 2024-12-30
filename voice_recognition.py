import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import json
import threading

class VoiceRecognitionSystem:
    def __init__(self, model_path="vosk-model-small-en-us-0.15"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.running = False
        self.callbacks = []

    def start_listening(self):
        self.running = True
        self.thread = threading.Thread(target=self._audio_callback)
        self.thread.start()

    def _audio_callback(self):
        with sd.InputStream(samplerate=16000, channels=1, 
                          dtype=np.int16, blocksize=8000) as stream:
            while self.running:
                audio, _ = stream.read(8000)
                if self.recognizer.AcceptWaveform(audio.tobytes()):
                    result = json.loads(self.recognizer.Result())
                    if result["text"]:
                        self._process_command(result["text"])

    def add_command_callback(self, callback):
        self.callbacks.append(callback)

    def stop_listening(self):
        self.running = False
        self.thread.join()
