# device_controller.py

from typing import Dict, Any, Optional, List
from device import Device
import json
import time
import re
from pathlib import Path

class DeviceController:
    def __init__(self, config_path: Optional[str] = None):
        self.devices: Dict[str, Device] = {}
        self._command_history: List[Dict[str, Any]] = []
        self._load_config(config_path) if config_path else None
    
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
    
    def _parse_and_execute(self, command: str) -> Dict[str, Any]:
        """Parse and execute a command"""
        command = command.lower()
        
        # Example command patterns
        patterns = {
            r"turn (on|off) (\w+) in (\w+)": self._handle_actuator_command,
            r"read (\w+) from (\w+)": self._handle_sensor_command,
            r"status (\w+)": self._handle_status_command,
            r"list devices": self._handle_list_command
        }
        
        for pattern, handler in patterns.items():
            match = re.match(pattern, command)
            if match:
                return handler(*match.groups()) if match.groups() else handler()
        
        raise ValueError(f"Unknown command format: {command}")
    
    def _handle_actuator_command(self, state: str, actuator: str, device: str) -> Dict[str, Any]:
        """Handle actuator control commands"""
        device_obj = self.get_device(device)  # Now case-insensitive
        if not device_obj:
            raise ValueError(f"Device not found: {device}")
        
        # Make actuator name matching case-insensitive
        actuator_obj = None
        for act_name, act in device_obj.actuators.items():
            if act_name.lower() == actuator.lower():
                actuator_obj = act
                actuator = act_name  # Use the correct case
                break
        
        if not actuator_obj:
            raise ValueError(f"Actuator not found: {actuator}")
        
        success = device_obj.control_actuator(actuator, state == "on")
        return {
            "type": "actuator_control",
            "device": device_obj.name,
            "actuator": actuator,
            "state": state,
            "success": success
        }
    
    def _handle_sensor_command(self, sensor: str, device: str) -> Dict[str, Any]:
        """Handle sensor reading commands"""
        device_obj = self.get_device(device)  # Now case-insensitive
        if not device_obj:
            raise ValueError(f"Device not found: {device}")
        
        # Make sensor name matching case-insensitive
        sensor_obj = None
        for sens_name, sens in device_obj.sensors.items():
            if sens_name.lower() == sensor.lower():
                sensor_obj = sens
                sensor = sens_name  # Use the correct case
                break
        
        if not sensor_obj:
            raise ValueError(f"Sensor not found: {sensor}")
        
        value = device_obj.read_sensor(sensor)
        return {
            "type": "sensor_read",
            "device": device_obj.name,
            "sensor": sensor,
            "value": value
        }
    
    def _handle_status_command(self, device: str) -> Dict[str, Any]:
        """Handle device status commands"""
        device_obj = self.get_device(device)  # Now case-insensitive
        if not device_obj:
            raise ValueError(f"Device not found: {device}")
        
        return {
            "type": "device_status",
            "device": device_obj.name,
            "state": device_obj.get_state()
        }
    
    def _handle_list_command(self) -> Dict[str, Any]:
        """Handle list devices command"""
        return {
            "type": "device_list",
            "devices": [
                {
                    "name": device.name,
                    "site": device.site,
                    "actuators": list(device.actuators.keys()),
                    "sensors": list(device.sensors.keys())
                }
                for device in self.devices.values()
            ]
        }
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a command and return the result"""
        try:
            result = self._parse_and_execute(command)
            self._log_command(command, result)
            return {
                "success": True,
                "command": command,
                "result": result
            }
        except Exception as e:
            error_result = {
                "success": False,
                "command": command,
                "error": str(e)
            }
            self._log_command(command, error_result)
            return error_result
    
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
