# device.py

from typing import Dict, Any, Optional, List
from device_components import Sensor, Actuator
import time
import json

class Device:
    """Represents a physical or virtual device with sensors and actuators"""
    
    def __init__(self, name: str, site: str):
        self.name = name
        self.site = site
        self.actuators: Dict[str, Actuator] = {}
        self.sensors: Dict[str, Sensor] = {}
        self._metadata: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
    
    def add_actuator(self, actuator: Actuator) -> None:
        """Add an actuator to the device"""
        self.actuators[actuator.name] = actuator
        self._log_event("actuator_added", {
            "name": actuator.name,
            "type": actuator.__class__.__name__
        })
    
    def add_sensor(self, sensor: Sensor) -> None:
        """Add a sensor to the device"""
        self.sensors[sensor.name] = sensor
        self._log_event("sensor_added", {
            "name": sensor.name,
            "type": sensor.__class__.__name__
        })
    
    def get_actuator(self, name: str) -> Optional[Actuator]:
        """Get an actuator by name"""
        return self.actuators.get(name)
    
    def get_sensor(self, name: str) -> Optional[Sensor]:
        """Get a sensor by name"""
        return self.sensors.get(name)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set device metadata"""
        self._metadata[key] = value
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """Get device metadata"""
        return self._metadata.get(key)
    
    def control_actuator(self, actuator_name: str, state: bool) -> bool:
        """Control an actuator's state"""
        actuator = self.get_actuator(actuator_name)
        if actuator:
            success = actuator.set(state)
            self._log_event("actuator_state_changed", {
                "name": actuator_name,
                "state": state,
                "success": success
            })
            return success
        return False
    
    def read_sensor(self, sensor_name: str) -> Optional[float]:
        """Read a sensor's value"""
        sensor = self.get_sensor(sensor_name)
        if sensor:
            reading = sensor.read()
            self._log_event("sensor_read", {
                "name": sensor_name,
                "value": reading.value,
                "unit": reading.unit
            })
            return reading.value
        return None
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of the device"""
        state = {
            "name": self.name,
            "site": self.site,
            "timestamp": time.time(),
            "actuators": {
                name: act.status for name, act in self.actuators.items()
            },
            "sensors": {
                name: sens.value for name, sens in self.sensors.items()
            },
            "metadata": self._metadata
        }
        return state
    
    def _log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log device events"""
        event = {
            "timestamp": time.time(),
            "device": self.name,
            "type": event_type,
            "details": details
        }
        self._history.append(event)
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get device event history"""
        if limit:
            return self._history[-limit:]
        return self._history
    
    def to_json(self) -> str:
        """Convert device state to JSON"""
        return json.dumps(self.get_state(), indent=2)
    
    def __str__(self) -> str:
        """String representation of the device"""
        return f"Device({self.name} at {self.site})"
