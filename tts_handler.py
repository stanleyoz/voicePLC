# tts_handler.py
import subprocess
import tempfile
import os
from typing import Optional
import threading
import queue

class TTSHandler:
    def __init__(self, 
                 voice: str = "en-us",
                 speed: float = 1.0,
                 pitch: int = 0):
        """Initialize TTS handler using espeak.
        
        Args:
            voice: Voice identifier for espeak
            speed: Speech rate multiplier
            pitch: Voice pitch adjustment
        """
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.speak_thread = None
        
    def _speak_worker(self):
        """Worker thread for processing speech queue."""
        while self.is_speaking:
            try:
                text = self.speech_queue.get(timeout=1)
                self._synthesize_speech(text)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in speech synthesis: {e}")
                
    def _synthesize_speech(self, text: str):
        """Synthesize speech using espeak."""
        try:
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech using espeak
            subprocess.run([
                'espeak',
                '-v', self.voice,
                '-s', str(int(self.speed * 175)),  # Default speed is 175 wpm
                '-p', str(self.pitch),
                '-w', temp_path,
                text
            ], check=True)
            
            # Play generated audio
            subprocess.run(['aplay', temp_path], check=True)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
        except subprocess.CalledProcessError as e:
            print(f"Error synthesizing speech: {e}")
        except Exception as e:
            print(f"Unexpected error in speech synthesis: {e}")
            
    def start(self):
        """Start the TTS handler."""
        if not self.is_speaking:
            self.is_speaking = True
            self.speak_thread = threading.Thread(target=self._speak_worker)
            self.speak_thread.start()
            
    def stop(self):
        """Stop the TTS handler."""
        if self.is_speaking:
            self.is_speaking = False
            self.speak_thread.join()
            
    def speak(self, text: str):
        """Queue text for speech synthesis.
        
        Args:
            text: Text to be spoken
        """
        if self.is_speaking:
            self.speech_queue.put(text)
            
    def is_active(self) -> bool:
        """Check if TTS handler is currently active."""
        return self.is_speaking

# Example usage
if __name__ == "__main__":
    tts = TTSHandler()
    tts.start()
    tts.speak("Hello, I am the voice PLC system. How can I help you today?")
    input("Press Enter to stop speaking...")
    tts.stop()
