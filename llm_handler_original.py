# llm_handler.py

from typing import Dict, Any, Optional, List
from llama_cpp import Llama
import json
from pathlib import Path

class LLMHandler:
    def __init__(self, model_path: str):
        """Initialize LLM with the specified model"""
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,            # Context window
            n_batch=512,           # Batch size for prompt processing
            n_threads=4            # Number of CPU threads to use
        )
        
        # Command templates for different actions
        self.action_templates = {
            "ACTUATOR_CONTROL": {
                "type": "actuator_control",
                "device": "",
                "actuator": "",
                "action": "on/off"
            },
            "SENSOR_READ": {
                "type": "sensor_read",
                "device": "",
                "sensor": ""
            },
            "STATUS_CHECK": {
                "type": "status_check",
                "device": "",
                "component": "all/specific"
            },
            "LIST_DEVICES": {
                "type": "list_devices"
            }
        }

    def generate_device_context(self, devices: Dict[str, Any]) -> str:
        """Generate context information about available devices"""
        context = "Available devices and their capabilities:\n"
        for device_name, device in devices.items():
            context += f"\n{device_name} at {device.site}:\n"
            context += f"- Actuators: {', '.join(device.actuators.keys())}\n"
            context += f"- Sensors: {', '.join(device.sensors.keys())}\n"
            if device._metadata:
                context += f"- Additional info: {json.dumps(device._metadata)}\n"
        return context

    def parse_command(self, command: str, context: str) -> Dict[str, Any]:
        """Parse natural language command into structured action"""
        
        prompt = f"""Current system state:
{context}

User command: "{command}"

Task: Parse this command into a structured action. The output should be valid JSON matching one of these templates:

1. For actuator control:
{json.dumps(self.action_templates["ACTUATOR_CONTROL"], indent=2)}

2. For sensor reading:
{json.dumps(self.action_templates["SENSOR_READ"], indent=2)}

3. For status check:
{json.dumps(self.action_templates["STATUS_CHECK"], indent=2)}

4. For listing devices:
{json.dumps(self.action_templates["LIST_DEVICES"], indent=2)}

Output only the JSON, no other text. If the command is unclear, include an "error" field in the JSON explaining why.

Response:"""

        # Get LLM response
        response = self.llm(
            prompt,
            max_tokens=512,
            stop=["```"],
            echo=False
        )

        try:
            # Extract JSON from response
            response_text = response["choices"][0]["text"].strip()
            return json.loads(response_text)
        except (json.JSONDecodeError, KeyError) as e:
            return {
                "error": f"Failed to parse command: {str(e)}",
                "raw_response": response_text
            }

    def generate_response(self, action_result: Dict[str, Any]) -> str:
        """Generate natural language response from action result"""
        
        prompt = f"""System action result:
{json.dumps(action_result, indent=2)}

Task: Generate a natural, friendly response describing the result of this action. 
Be concise but informative. Include any relevant values or status information.
If there was an error, explain it clearly.

Response:"""

        response = self.llm(
            prompt,
            max_tokens=256,
            stop=["```"],
            echo=False
        )
        
        return response["choices"][0]["text"].strip()

    def enhance_error_message(self, error: str) -> str:
        """Generate a more helpful error message"""
        
        prompt = f"""Error message: "{error}"

Task: Provide a more user-friendly explanation of this error and suggest how to fix it.
Keep it concise but helpful.

Response:"""

        response = self.llm(
            prompt,
            max_tokens=128,
            stop=["```"],
            echo=False
        )
        
        return response["choices"][0]["text"].strip()
