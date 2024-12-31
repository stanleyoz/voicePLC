# device_components.py
from abc import ABC, abstractmethod
import random
from typing import Any, Dict, List, Optional
import json

class Device(ABC):
    def __init__(self, config: Dict[str, Any], mock: bool = False):
        """Initialize device from configuration
        
        Args:
            config: Device configuration dictionary
            mock: Whether to use mock values
        """
        self.id = config["id"]
        self.type = config["type"]
        self.description = config.get("description", "")
        self.mock = mock
        self._config = config
        self._setup()
    
    @abstractmethod
    def _setup(self):
        """Setup device specific configuration"""
        pass
        
    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """Read current device state"""
        pass
        
    def get_status(self) -> Dict[str, Any]:
        """Get device status information"""
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "state": self.read()
        }

class Sensor(Device):
    def _setup(self):
        """Setup sensor configuration"""
        self.unit = self._config["unit"]
        self.range = self._config["range"]
        if self.mock:
            self.mock_range = self._config.get("mock_range", self.range)
            
    def read(self) -> Dict[str, Any]:
        """Read sensor value"""
        if self.mock:
            value = random.uniform(self.mock_range[0], self.mock_range[1])
            # Round based on sensor type
            if self.type in ["temperature", "pressure", "level"]:
                value = round(value, 2)
            elif self.type in ["flow", "power"]:
                value = round(value, 1)
            elif self.type == "energy":
                value = round(value, 0)
            
            return {
                "value": value,
                "unit": self.unit
            }
        else:
            raise NotImplementedError("Real sensor implementation required")

class Actuator(Device):
    def _setup(self):
        """Setup actuator configuration"""
        self.valid_states = self._config["states"]
        self.state = self._config.get("initial_state", self.valid_states[0])
                
    def read(self) -> Dict[str, Any]:
        """Read actuator state"""
        return {"state": self.state}
        
    def set_value(self, value: str) -> Dict[str, Any]:
        """Set actuator state"""
        value = value.upper()
        if value in self.valid_states:
            self.state = value
            return {"state": self.state}
        else:
            raise ValueError(f"Invalid state: {value}. Valid states: {self.valid_states}")

class DeviceManager:
    def __init__(self, config_file: str, mock: bool = False):
        """Initialize device manager from configuration file
        
        Args:
            config_file: Path to devices.json configuration file
            mock: Whether to use mock devices
        """
        self.mock = mock
        self.devices: Dict[str, Device] = {}
        self._load_config(config_file)
        
    def _load_config(self, config_file: str):
        """Load device configuration from file"""
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        # Load sensors
        for sensor_id, sensor_config in config.get("sensors", {}).items():
            self.devices[sensor_id] = Sensor(sensor_config, mock=self.mock)
            
        # Load actuators
        for actuator_id, actuator_config in config.get("actuators", {}).items():
            self.devices[actuator_id] = Actuator(actuator_config, mock=self.mock)
            
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)
        
    def get_all_devices(self) -> Dict[str, Device]:
        """Get all devices"""
        return self.devices
        
    def get_devices_by_type(self, device_type: str) -> List[Device]:
        """Get all devices of a specific type"""
        return [device for device in self.devices.values() if device.type == device_type]
