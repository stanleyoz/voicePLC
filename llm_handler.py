# llm_handler.py

from typing import Dict, Any, Optional, List
from llama_cpp import Llama
import json
from pathlib import Path

class LLMHandler:
    def __init__(self, model_path: str):
        """Initialize LLM with optimized parameters"""
        self.llm = Llama(
            model_path=model_path,
            n_ctx=512,            
            n_batch=8,            
            n_threads=4,          
            n_gpu_layers=0        
        )
        
        # Simplified command templates
        self.action_templates = {
            "sensor_read": {
                "type": "sensor_read",
                "device": "watersystem",
                "sensor": "watertemp"
            },
            "actuator_control": {
                "type": "actuator_control",
                "device": "watersystem",
                "actuator": "mainpump",
                "state": "on"
            },
            "status_check": {
                "type": "status_check",
                "device": "watersystem"
            },
            "list_devices": {
                "type": "list_devices"
            }
        }

    def generate_device_context(self, devices: Dict[str, Any]) -> str:
        """Generate simplified context"""
        context_lines = []
        for name, device in devices.items():
            context_lines.extend([
                f"Device: {name}",
                f"Location: {device.site}",
                f"Sensors: {', '.join(device.sensors.keys())}",
                f"Actuators: {', '.join(device.actuators.keys())}",
                ""
            ])
        return "\n".join(context_lines)

    def parse_command(self, command: str, context: str) -> Dict[str, Any]:
        """Parse command with robust error handling"""
        prompt = f"""Current system context:
{context}

User command: "{command}"

Task: Parse this command into a structured response.
- If asking about temperature, sensor readings, or flow -> use "sensor_read"
- If asking about status -> use "status_check"
- If asking about turning things on/off -> use "actuator_control"
- If asking about location -> use "status_check"
- If asking about site, description, or other properties -> use "property_query"

Return a JSON object matching one of these examples:
For property queries:
{{
    "type": "property_query",
    "device": "WaterSystem",
    "property": "site"  # or "location", "description", etc.
}}

For temperature query:
{{
    "type": "sensor_read",
    "device": "WaterSystem",
    "sensor": "WaterTemp"
}}

For status query:
{{
    "type": "status_check",
    "device": "WaterSystem"
}}

Response (in JSON format):"""

        try:
            # Get LLM response with strict JSON formatting
            response = self.llm(
                prompt,
                max_tokens=128,
                stop=["}"], # Stop after JSON object
                echo=False,
                temperature=0.1
            )

            response_text = response["choices"][0]["text"].strip()
            if not response_text.endswith("}"):
                response_text += "}"
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback to status check if parsing fails
                return {
                    "type": "sensor_read",
                    "device": "WaterSystem",
                    "sensor": "WaterTemp"
                }

        except Exception as e:
            return {
                "type": "error",
                "message": str(e)
            }

    def generate_response(self, action_result: Dict[str, Any]) -> str:
        """Generate natural, focused response based on action type and result"""
        try:
            if 'state' in action_result.get('result', {}):
                state = action_result['result']['state']
                
                # Location query
                if 'location' in state.get('metadata', {}):
                    return f"The MainPump is located in {state['metadata']['location']} in {state['site']}"
                
                # Status query
                if state.get('actuators', {}):
                    actuator_status = []
                    for name, status in state['actuators'].items():
                        actuator_status.append(f"{name} is {'ON' if status else 'OFF'}")
                    return ", ".join(actuator_status)
                
                # Sensor readings
                if state.get('sensors', {}):
                    sensor_readings = []
                    for name, value in state['sensors'].items():
                        if name == "WaterTemp":
                            sensor_readings.append(f"Temperature is {value}°C")
                        elif name == "MainFlow":
                            sensor_readings.append(f"Flow rate is {value} L/min")
                    return ", ".join(sensor_readings)

            # Specific response for sensor read type
            if action_result.get('result', {}).get('type') == 'sensor_read':
                value = action_result['result'].get('value', 'unavailable')
                unit = action_result['result'].get('unit', '')
                sensor = action_result['result'].get('sensor', '')
                return f"{sensor} reading is {value} {unit}"

            # List devices response
            if action_result.get('result', {}).get('type') == 'list_devices':
                devices = action_result['result'].get('devices', [])
                device_names = [d['name'] for d in devices]
                return f"Available devices: {', '.join(device_names)}"

            # Actuator control response
            if action_result.get('result', {}).get('type') == 'actuator_control':
                actuator = action_result['result'].get('actuator', '')
                state = action_result['result'].get('state', '')
                return f"{actuator} has been turned {state}"

            # Default response if no specific format matches
            return str(action_result.get('result', 'Command processed'))

        except Exception as e:
            return f"Error processing response: {str(e)}"

    def enhance_error_message(self, error: str) -> str:
        """Provide clear error message"""
        basic_errors = {
            "JSONDecodeError": "Could not understand the command. Please try rephrasing.",
            "KeyError": "Missing required information. Please specify the device or action.",
            "ValueError": "Invalid command format. Please try again.",
        }
        
        for error_type, message in basic_errors.items():
            if error_type in error:
                return message
        
        return "Could not process command. Please try rephrasing."
