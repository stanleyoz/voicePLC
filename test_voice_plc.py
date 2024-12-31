# test_voice_plc.py
from voice_handler import VoiceHandler
from device_controller import DeviceController
from tts_handler import TTSHandler
import time
import argparse
from rich.console import Console
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
console = Console()

class VoicePLCTester:
    def __init__(self, model_path: str, vosk_model_path: str, config_file: str, use_gpu: bool = False, gpu_layers: int = None):
        """Initialize test components"""
        logger.info("Initializing VoicePLC Tester...")
        
        # Initialize device controller with config
        logger.info("Setting up Device Controller...")
        self.controller = DeviceController(
            model_path=model_path,
            config_file=config_file,
            mock=True,
            use_gpu=use_gpu,
            gpu_layers=gpu_layers
        )
        
        # Initialize TTS
        logger.info("Setting up TTS Handler...")
        self.tts = TTSHandler()
        self.tts.start()
        
        # Initialize voice recognition with command callback
        logger.info("Setting up Voice Handler...")
        self.voice = VoiceHandler(
            model_path=vosk_model_path,
            callback=self.handle_voice_command
        )
        logger.info("Initialization complete.")
    
    def handle_voice_command(self, text: str):
        """Process voice command through LLM and speak response"""
        try:
            logger.info(f"Processing voice command: {text}")
            console.print(f"[cyan]Recognized: {text}[/cyan]")
            
            # Process command through LLM
            logger.debug("Sending to LLM for processing...")
            response = self.controller.process_command(text)
            logger.info(f"LLM Response received: {response}")
            console.print(f"[green]Response: {response}[/green]")
            
            # Speak response
            logger.debug("Sending to TTS...")
            self.tts.speak(str(response))
            
        except Exception as e:
            error_msg = f"Error in command processing: {str(e)}"
            logger.error(error_msg)
            console.print(f"[red]{error_msg}[/red]")
            self.tts.speak(f"Error processing command: {str(e)}")
    
    def start(self):
        """Start voice command processing"""
        logger.info("Starting VoicePLC system...")
        console.print("[yellow]Starting voice recognition...[/yellow]")
        console.print("Speak commands or press Ctrl+C to exit")
        console.print("\nTry commands like:")
        console.print("- What's the inlet pressure?")
        console.print("- Check pump 1 bearing temperature")
        console.print("- Turn pump 2 on")
        console.print("- What's the station power consumption?")
        console.print("- Get the wet well level")
        
        self.voice.start_listening()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Shutdown initiated...")
            console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            logger.info("Stopping components...")
            self.voice.stop_listening()
            self.tts.stop()
            logger.info("Shutdown complete.")

def main():
    parser = argparse.ArgumentParser(description='Voice PLC Test with GPU support')
    parser.add_argument('--gpu', action='store_true', help='Enable GPU acceleration')
    parser.add_argument('--gpu-layers', type=int, help='Number of layers to offload to GPU')
    parser.add_argument('--model', default='models/mistral-7b-instruct-v0.2.Q4_K_M.gguf',
                       help='Path to LLM model')
    parser.add_argument('--vosk-model', default='models/vosk-model-small-en-us-0.15',
                       help='Path to Vosk model')
    parser.add_argument('--config', default='devices.json',
                       help='Path to devices configuration file')
    
    args = parser.parse_args()
    
    if args.gpu:
        logger.info("GPU mode enabled")
        console.print("[yellow]Running with GPU acceleration...[/yellow]")
        if args.gpu_layers:
            console.print(f"[yellow]Using {args.gpu_layers} GPU layers[/yellow]")
    else:
        logger.info("Running in CPU-only mode")
        console.print("[yellow]Running in CPU-only mode[/yellow]")
    
    try:
        tester = VoicePLCTester(
            model_path=args.model,
            vosk_model_path=args.vosk_model,
            config_file=args.config,
            use_gpu=args.gpu,
            gpu_layers=args.gpu_layers
        )
        tester.start()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        console.print(f"[red]Critical error: {str(e)}[/red]")

if __name__ == "__main__":
    main()
