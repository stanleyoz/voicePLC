# voicePLC - LLM Version

This version implements LLM (Large Language Model) support using llamafile/llama.cpp for 
natural language processing of device control commands.

## Features
- Natural language command processing using Mistral 7B model
- JSON and natural language response modes
- Support for device queries including:
  - Location queries
  - Status checks
  - Sensor readings
  - Actuator control
  - Property queries

## Model
- Using Mistral 7B Instruct v0.2 quantized
- Model file: mistral-7b-instruct-v0.2.Q4_K_M.gguf

## Command Examples
command what is the temperature of watersystem
command where is the mainpump located
command turn on the main pump
command what is watersystem's site

Response Modes

1. LLM (Natural Language):

python main.py --simulation --response-mode llm

2. JSON (Raw Data):

python main.py --simulation --response-mode json
