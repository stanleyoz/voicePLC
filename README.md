# VoicePLC

A voice-controlled Programmable Logic Controller (PLC) interface using LLM (Large Language Model) for natural language command processing.

## Features

- Voice command recognition using Vosk
- LLM-powered command interpretation using Mistral 7B
- Text-to-speech response using espeak
- GPU/CPU flexible operation
- Mock device simulation for testing
- Configurable device setup via JSON

## System Requirements

- Ubuntu 22.04 (WSL2 supported)
- Python 3.10+
- CUDA support (optional for GPU acceleration)

## Installation

1. Install system dependencies:
```bash
# System Dependencies (Ubuntu 22.04 WSL)
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake git python3-pip python3-dev
sudo apt install -y libportaudio2 libsndfile1
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y ffmpeg
sudo apt install -y espeak
```

2. Create and activate conda environment:
```bash
conda create -n voicePLC python=3.10
conda activate voicePLC
```

3. Install required conda packages:
```bash
# Conda Packages
conda install -c conda-forge numpy
conda install -c pytorch pytorch cpuonly
conda install -c conda-forge rich
conda install -c conda-forge portaudio
conda install -c conda-forge pyaudio
conda install -c conda-forge requests
conda install -c conda-forge pytz
conda install -c conda-forge six
conda install -c conda-forge packaging
```

4. Install required pip packages:
```bash
# Pip Packages
pip install sounddevice
pip install vosk==0.3.45
pip install requests
pip install idna
pip install transformers
pip install optimum
pip install auto-gptq
pip install llama-cpp-python
```

5. Download required models:
```bash
# Create models directory
mkdir -p models

# Download Mistral 7B model
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -O models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Download Vosk model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/
```

## Project Structure

```
voicePLC/
├── models/
│   ├── mistral-7b-instruct-v0.2.Q4_K_M.gguf
│   └── vosk-model-small-en-us-0.15/
├── device_components.py
├── device.py
├── device_controller.py
├── llm_handler.py
├── main.py
├── voice_handler.py
├── tts_handler.py
├── devices.json
└── README.md
```

## Usage

1. Basic usage (CPU mode):
```bash
python main.py
```

2. With GPU acceleration:
```bash
python main.py --gpu
```

3. With specific GPU layers:
```bash
python main.py --gpu --gpu-layers 32
```

4. Testing components:
```bash
# Test speech recognition
python test_stt.py

# Test command processing
python test_command.py

# Test text-to-speech
python test_tts.py
```

## Voice Commands

Example commands:
- "What is the temperature of sensor 1?"
- "Turn actuator 1 on"
- "Get the pressure from sensor 2"
- "Check the status of pump 1"

## Device Configuration

Devices can be configured in the `devices.json` file with the following structure:
```json
{
    "sensors": {
        "sensor_id": {
            "id": "sensor_id",
            "type": "sensor_type",
            "unit": "measurement_unit",
            "range": [min, max],
            "description": "sensor_description"
        }
    },
    "actuators": {
        "actuator_id": {
            "id": "actuator_id",
            "type": "actuator_type",
            "states": ["state1", "state2"],
            "description": "actuator_description"
        }
    }
}
```

## License

MIT License

## Contributors

- Stanley Oz

## Version History

- v1.0-regex: Initial version with regex command parsing
- v1.1-llm: LLM integration for natural language processing
- v1.2-voice: Voice command support with GPU acceleration
