# device_controller.py

from typing import Dict, Any, Optional, List
from device import Device
import json
import time
import re
from pathlib import Path
from llm_handler import LLMHandler


# device_controller.py (updated init and process_command)

class DeviceController:
    def __init__(self, model_path: str, llm_response: bool = True, config_path: Optional[str] = None):
        """Initialize the device controller with LLM support
        
        Args:
            model_path: Path to the LLM model file
            llm_response: If True, generate natural language responses
            config_path: Optional path to config file
        """
        self.devices: Dict[str, Device] = {}
        self._command_history: List[Dict[str, Any]] = []
        self.llm_response = llm_response
        self.llm_handler = LLMHandler(model_path)
        if config_path:
            self._load_config(config_path)

    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a natural language command using LLM"""
        try:
            context = self.llm_handler.generate_device_context(self.devices)
            action = self.llm_handler.parse_command(command, context)
            
            if "error" in action:
                return {
                    "success": False,
                    "command": command,
                    "error": self.llm_handler.enhance_error_message(action["error"])
                }
            
            result = self._execute_action(action)
            
            response = {
                "success": True,
                "command": command,
                "result": result,
            }

            if self.llm_response:
                # Generate natural language response if flag is True
                nl_response = self.llm_handler.generate_response({"result": result})
                response["response"] = nl_response
            else:
                # Return raw result if flag is False
                response["response"] = result
            
            self._log_command(command, response)
            return response
            
        except Exception as e:
            error_result = {
                "success": False,
                "command": command,
                "error": str(e)
            }
            self._log_command(command, error_result)
            return error_result

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parsed action"""
        action_type = action.get("type")
        
        if action_type == "actuator_control":
            return self._handle_actuator_action(action)
        elif action_type == "sensor_read":
            return self._handle_sensor_action(action)
        elif action_type == "status_check":
            return self._handle_status_action(action)
        elif action_type == "list_devices":
            return self._handle_list_action()
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def _handle_actuator_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle actuator control action"""
        device = self.get_device(action["device"])
        if not device:
            raise ValueError(f"Device not found: {action['device']}")
        
        success = device.control_actuator(
            action["actuator"], 
            action["action"].lower() == "on"
        )
        
        return {
            "type": "actuator_control",
            "device": device.name,
            "actuator": action["actuator"],
            "state": action["action"],
            "success": success
        }

    def _handle_sensor_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sensor reading action"""
        device = self.get_device(action["device"])
        if not device:
            raise ValueError(f"Device not found: {action['device']}")
        
        value = device.read_sensor(action["sensor"])
        sensor = device.get_sensor(action["sensor"])
        
        return {
            "type": "sensor_read",
            "device": device.name,
            "sensor": action["sensor"],
            "value": value,
            "unit": sensor.unit if sensor else None
        }

    def _handle_status_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status check action"""
        device = self.get_device(action["device"])
        if not device:
            raise ValueError(f"Device not found: {action['device']}")
        
        return {
            "type": "status_check",
            "device": device.name,
            "state": device.get_state()
        }

    def _handle_list_action(self) -> Dict[str, Any]:
        """Handle list devices action"""
        return {
            "type": "list_devices",
            "devices": [
                {
                    "name": device.name,
                    "site": device.site,
                    "actuators": list(device.actuators.keys()),
                    "sensors": list(device.sensors.keys()),
                    "metadata": device._metadata
                }
                for device in self.devices.values()
            ]
        }

    def _log_command(self, command: str, result: Dict[str, Any]) -> None:
        """Log processed commands"""
        self._command_history.append({
            "timestamp": time.time(),
            "command": command,
            "result": result
        })

    def get_command_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get command history"""
        if limit:
            return self._command_history[-limit:]
        return self._command_history

    def _load_config(self, config_path: str) -> None:
        """Load device configuration from file"""
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
    
    def add_device(self, device: Device) -> None:
        """Add a device to the controller"""
        self.devices[device.name] = device

    def get_device(self, name: str) -> Optional[Device]:
        """Get a device by name (case-insensitive)"""
        name_lower = name.lower()
        for device_name, device in self.devices.items():
            if device_name.lower() == name_lower:
                return device
        return None
