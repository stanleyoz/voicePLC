# device_controller.py
from typing import Dict, Any, Optional, Union
from device_components import DeviceManager, Sensor, Actuator
from llm_handler import LLMHandler
import json
import logging

class DeviceController:
    def __init__(
        self,
        model_path: str,
        config_file: str = "devices.json",
        mock: bool = False,
        n_threads: Optional[int] = None,
        use_gpu: bool = False,
        gpu_layers: Optional[int] = None
    ):
        """Initialize the device controller"""
        # Initialize LLM handler
        self.llm = LLMHandler(
            model_path=model_path,
            n_threads=n_threads,
            use_gpu=use_gpu,
            gpu_layers=gpu_layers
        )
        
        # Initialize device manager
        self.device_manager = DeviceManager(config_file, mock=mock)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def process_command(
        self,
        command: str,
        response_format: str = "text"
    ) -> Union[str, Dict[str, Any]]:
        """Process a command using LLM and execute device operations"""
        try:
            # Get LLM interpretation
            llm_response = self.llm.generate_response(
                command,
                response_format="json"
            )
            
            if "error" in llm_response:
                return f"Error: {llm_response['error']}"

            # Get device action
            device_id = self._map_device_name(llm_response.get("device", ""))
            if not device_id:
                return "Could not identify the device in your command"

            # Execute action
            action = llm_response.get("command", "").lower()
            value = llm_response.get("value")
            
            device = self.device_manager.get_device(device_id)
            if not device:
                return f"Device {device_id} not found"

            # Handle the action
            if action == "read":
                result = device.read()
                return self._format_read_response(device, result)
            elif action == "set":
                if not hasattr(device, 'set_value'):
                    return f"Cannot control {device_id} - read-only device"
                result = device.set_value(value)
                return f"Set {device.description} to {result.get('state', value)}"
            else:
                return f"Unknown command: {action}"

        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return f"Error processing command: {str(e)}"

    def _map_device_name(self, device_name: str) -> str:
        """Map common device names to actual device IDs"""
        # Direct mapping if exact match
        if device_name in self.device_manager.devices:
            return device_name

        # Handle common variations
        name_lower = device_name.lower()
        mapping = {
            "pump1": ["pump 1", "pump one", "first pump"],
            "pump2": ["pump 2", "pump two", "second pump"],
            "temp_pump1": ["pump 1 temperature", "first pump temperature"],
            "temp_pump2": ["pump 2 temperature", "second pump temperature"],
            "pressure_in": ["inlet pressure", "input pressure"],
            "pressure_out": ["outlet pressure", "output pressure"],
            "power_meter": ["power", "power consumption"],
            "energy_meter": ["energy", "energy consumption"],
            "level_sensor": ["level", "water level", "well level"]
        }

        for device_id, variants in mapping.items():
            if any(variant in name_lower for variant in variants):
                return device_id

        return ""

    def _format_read_response(self, device: Union[Sensor, Actuator], result: Dict[str, Any]) -> str:
        """Format the read response based on device type"""
        if "value" in result and "unit" in result:
            return f"{device.description}: {result['value']} {result['unit']}"
        elif "state" in result:
            return f"{device.description} is {result['state']}"
        return f"Current value of {device.description}: {result}"
