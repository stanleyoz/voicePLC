# voice_handler.py
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import json
import threading
from typing import Callable, Optional

class VoiceHandler:
    def __init__(self, 
                 model_path: str = "vosk-model-small-en-us-0.15",
                 sample_rate: int = 16000,
                 callback: Optional[Callable] = None):
        """Initialize voice handler with Vosk model and audio settings.
        
        Args:
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate (Hz)
            callback: Optional callback for processed commands
        """
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.callback = callback
        
        # Audio stream configuration
        self.stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16,
            callback=self._audio_callback
        )
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream processing."""
        if status:
            print(f"Audio callback status: {status}")
        if self.is_listening:
            self.audio_queue.put(bytes(indata))
            
    def _process_audio(self):
        """Process audio data from queue and perform recognition."""
        while self.is_listening:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                if self.recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self.recognizer.Result())
                    if result.get("text") and self.callback:
                        self.callback(result["text"])
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
                
    def start_listening(self):
        """Start audio capture and processing."""
        if not self.is_listening:
            self.is_listening = True
            self.stream.start()
            self.process_thread = threading.Thread(target=self._process_audio)
            self.process_thread.start()
            
    def stop_listening(self):
        """Stop audio capture and processing."""
        if self.is_listening:
            self.is_listening = False
            self.stream.stop()
            self.process_thread.join()
            
    def is_active(self) -> bool:
        """Check if voice handler is currently active."""
        return self.is_listening

# Example usage function
def handle_voice_command(command: str):
    """Example callback for processing voice commands."""
    print(f"Received command: {command}")
    
if __name__ == "__main__":
    # Test voice handler
    handler = VoiceHandler(callback=handle_voice_command)
    handler.start_listening()
    input("Press Enter to stop listening...")
    handler.stop_listening()
