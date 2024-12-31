# test_stt.py
from voice_handler import VoiceHandler
import time

def print_command(text):
    """Simple callback to print recognized text"""
    print(f"\nRecognized: {text}")

def main():
    # Initialize voice handler
    handler = VoiceHandler(
        model_path="models/vosk-model-small-en-us-0.15",
        callback=print_command
    )
    
    print("Starting speech recognition...")
    print("Speak into your microphone (Ctrl+C to stop)")
    
    try:
        handler.start_listening()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        handler.stop_listening()

if __name__ == "__main__":
    main()
