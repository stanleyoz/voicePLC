# device_components.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
import time

@dataclass
class DeviceReading:
    """Base class for sensor readings"""
    timestamp: float
    value: Any
    unit: str

class Sensor(ABC):
    """Abstract base class for all sensors"""
    def __init__(self, name: str, pin: Optional[int] = None):
        self.name = name
        self.pin = pin
        self._value = None
        self.unit = ""
        self._setup()
    
    @abstractmethod
    def _setup(self):
        """Initialize the sensor hardware or simulation"""
        pass
    
    @abstractmethod
    def read(self) -> DeviceReading:
        """Read current sensor value"""
        pass
    
    @property
    def value(self) -> Any:
        return self._value

class Actuator(ABC):
    """Abstract base class for all actuators"""
    def __init__(self, name: str, pin: Optional[int] = None):
        self.name = name
        self.pin = pin
        self._status = False
        self._setup()
    
    @abstractmethod
    def _setup(self):
        """Initialize the actuator hardware or simulation"""
        pass
    
    @abstractmethod
    def set(self, state: bool) -> bool:
        """Set actuator state"""
        pass
    
    @property
    def status(self) -> bool:
        return self._status

class MockSensor(Sensor):
    """Mock sensor for testing"""
    def __init__(self, name: str, unit: str = "units"):
        super().__init__(name)
        self.unit = unit
        self._value = 0.0
    
    def _setup(self):
        pass
    
    def read(self) -> DeviceReading:
        import random
        self._value = random.uniform(0, 100)
        return DeviceReading(
            timestamp=time.time(),
            value=self._value,
            unit=self.unit
        )

class MockActuator(Actuator):
    """Mock actuator for testing"""
    def __init__(self, name: str):
        super().__init__(name)
    
    def _setup(self):
        pass
    
    def set(self, state: bool) -> bool:
        self._status = state
        return True

# Example concrete implementations
class FlowMeter(MockSensor):
    """Flow meter sensor implementation"""
    def __init__(self, name: str, pin: Optional[int] = None):
        super().__init__(name, unit="L/min")

class Pump(MockActuator):
    """Pump actuator implementation"""
    def __init__(self, name: str, pin: Optional[int] = None):
        super().__init__(name)
        self.pin = pin

class TemperatureSensor(MockSensor):
    """Temperature sensor implementation"""
    def __init__(self, name: str, pin: Optional[int] = None):
        super().__init__(name, unit="°C")

class Valve(MockActuator):
    """Valve actuator implementation"""
    def __init__(self, name: str, pin: Optional[int] = None):
        super().__init__(name)
        self.pin = pin
