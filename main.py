# main.py
import argparse
import sys
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from device_controller import DeviceController
from voice_handler import VoiceHandler
from tts_handler import TTSHandler
import signal
import threading

console = Console()

class VoicePLC:
    def __init__(self, 
                 model_path: str,
                 vosk_model_path: str,
                 mock: bool = False,
                 use_gpu: bool = False,
                 gpu_layers: Optional[int] = None):
        """Initialize VoicePLC system.
        
        Args:
            model_path: Path to LLM model
            vosk_model_path: Path to Vosk speech recognition model
            mock: Use mock devices if True
        """
        self.controller = DeviceController(
            model_path=model_path, 
            mock=mock,
            use_gpu=use_gpu,
            gpu_layers=gpu_layers
        )
        self.tts = TTSHandler()
        
        # Initialize voice handler with callback to process_command
        self.voice = VoiceHandler(
            model_path=vosk_model_path,
            callback=self.process_command
        )
        
        self.running = False
        
    def process_command(self, command: str):
        """Process voice commands through the controller.
        
        Args:
            command: Voice command text
        """
        try:
            response = self.controller.process_command(command)
            if isinstance(response, str):
                self.tts.speak(response)
            elif isinstance(response, dict):
                self.tts.speak(response.get('message', 'Command processed'))
        except Exception as e:
            error_msg = f"Error processing command: {e}"
            console.print(f"[red]{error_msg}[/red]")
            self.tts.speak(error_msg)
            
    def start(self):
        """Start the VoicePLC system."""
        self.running = True
        self.tts.start()
        self.voice.start_listening()
        
        console.print("[green]VoicePLC system started[/green]")
        self.tts.speak("Voice PLC system is ready for commands")
        
        # Wait for shutdown signal
        try:
            while self.running:
                command = Prompt.ask("\nEnter command (or 'quit' to exit)")
                if command.lower() == 'quit':
                    break
                self.process_command(command)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            
    def stop(self):
        """Stop the VoicePLC system."""
        self.running = False
        self.voice.stop_listening()
        self.tts.stop()
        console.print("[yellow]VoicePLC system stopped[/yellow]")

def main():
    parser = argparse.ArgumentParser(description='VoicePLC Control System')
    parser.add_argument('--model', 
                       default='models/mistral-7b-instruct-v0.2.Q4_K_M.gguf',
                       help='Path to LLM model file')
    parser.add_argument('--vosk-model',
                       default='models/vosk-model-small-en-us-0.15',
                       help='Path to Vosk model directory')
    parser.add_argument('--mock',
                       action='store_true',
                       help='Use mock devices')
    parser.add_argument('--gpu',
                       action='store_true',
                       help='Enable GPU acceleration')
    parser.add_argument('--gpu-layers',
                       type=int,
                       help='Number of layers to offload to GPU (default: all)',
                       default=None)
    
    args = parser.parse_args()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        console.print("\n[yellow]Shutting down...[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start VoicePLC system
    # Configure GPU settings
    if args.gpu:
        console.print("[yellow]Starting with GPU acceleration...[/yellow]")
        if args.gpu_layers:
            console.print(f"[yellow]Using {args.gpu_layers} GPU layers[/yellow]")
    else:
        console.print("[yellow]Running in CPU-only mode[/yellow]")

    plc = VoicePLC(
        model_path=args.model,
        vosk_model_path=args.vosk_model,
        mock=args.mock,
        use_gpu=args.gpu,
        gpu_layers=args.gpu_layers
    )
    
    plc.start()

if __name__ == "__main__":
    main()
