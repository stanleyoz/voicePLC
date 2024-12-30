# voicePLC

Voice-controlled PLC system using Python and LLMs. This system allows control of devices, actuators, and sensors through natural language commands.

## Current Version Status
Current implementation uses regex-based command processing, with planned upgrade to LLM-based natural language processing.

## System Features
- Device management with actuators and sensors
- Command-line interface for testing
- Voice command capability (in development)
- Support for multiple devices and device types
- Real-time sensor monitoring
- Extensible architecture for new device types

## Installation

### System Requirements
- Ubuntu 22.04 (tested on WSL)
- Python 3.10
- Conda package manager

### Dependencies Installation

1. System Dependencies:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y build-essential cmake git python3-pip python3-dev
sudo apt install -y libportaudio2 libsndfile1
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y ffmpeg
```

2. Conda Environment Setup:
```bash
# Create and activate conda environment
conda create -n device_control python=3.10
conda activate device_control

# Install conda packages
conda install -c conda-forge numpy
conda install -c pytorch pytorch cpuonly
conda install -c conda-forge rich
conda install -c conda-forge portaudio
conda install -c conda-forge pyaudio
conda install -c conda-forge requests
conda install -c conda-forge pytz
conda install -c conda-forge six
conda install -c conda-forge packaging

# Install pip packages
pip install sounddevice
pip install vosk==0.3.45
pip install requests
pip install idna
pip install transformers
pip install optimum 
pip install auto-gptq
pip install llama-cpp-python
```

## Usage

### Starting the System
1. Activate the conda environment:
```bash
conda activate device_control
```

2. Run the dependency test:
```bash
python test_dependencies.py
```

3. Start the simulator:
```bash
python main.py --simulation
```

### Available Commands
The system currently supports the following command patterns:

1. List available devices:
```
command list devices
```

2. Check device status:
```
command status WaterSystem
```

3. Control actuators:
```
command turn on MainPump in WaterSystem
command turn off MainPump in WaterSystem
```

4. Read sensor values:
```
command read MainFlow from WaterSystem
command read WaterTemp from WaterSystem
```

5. View command history:
```
command history
```

### Supported Devices
Currently implemented device types:
- Water System (pumps, valves, flow meters, temperature sensors)
- HVAC System (circulators, temperature sensors)

## Project Structure
```
voicePLC/
├── device_components.py    # Base classes for Sensor, Actuator
├── device.py              # Device class implementation
├── device_controller.py   # Controller with regex command processing
├── cli_simulator.py       # CLI interface for testing
├── main.py               # Main program entry point
├── test_dependencies.py  # Dependency verification
└── voice_recognition.py  # Voice input processing
```

## Development Roadmap
- [x] Basic device control framework
- [x] Command-line interface
- [x] Regex-based command processing
- [ ] LLM integration for natural language processing
- [ ] Voice command processing
- [ ] Hardware integration
- [ ] Web interface

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Built using Python and various open-source libraries
- Tested on Ubuntu 22.04 WSL
