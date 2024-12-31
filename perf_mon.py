# performance_monitor.py
import time
import psutil
import threading
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import json
import os

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    gpu_utilization: float = 0.0  # Only used when GPU is enabled
    response_time: float = 0.0
    tokens_per_second: float = 0.0

class PerformanceMonitor:
    def __init__(self, log_file: str = "performance_log.json"):
        """Initialize performance monitor.
        
        Args:
            log_file: Path to performance log file
        """
        self.log_file = log_file
        self.metrics: List[PerformanceMetrics] = []
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent
            )
            
            # Try to get GPU metrics if available
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                metrics.gpu_utilization = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            except:
                pass
                
            self.metrics.append(metrics)
            time.sleep(1)  # Sample every second
            
    def record_inference(self, tokens: int, duration: float):
        """Record inference performance metrics.
        
        Args:
            tokens: Number of tokens processed
            duration: Processing duration in seconds
        """
        if self.metrics:
            self.metrics[-1].tokens_per_second = tokens / duration if duration > 0 else 0
            self.metrics[-1].response_time = duration
            
    def save_metrics(self):
        """Save performance metrics to log file."""
        metrics_data = [
            {
                "timestamp": m.timestamp,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "gpu_utilization": m.gpu_utilization,
                "response_time": m.response_time,
                "tokens_per_second": m.tokens_per_second
            }
            for m in self.metrics
        ]
        
        with open(self.log_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
            
    def get_summary(self) -> Dict[str, float]:
        """Get summary of performance metrics.
        
        Returns:
            Dictionary with average metrics
        """
        if not self.metrics:
            return {}
            
        return {
            "avg_cpu_percent": sum(m.cpu_percent for m in self.metrics) / len(self.metrics),
            "avg_memory_percent": sum(m.memory_percent for m in self.metrics) / len(self.metrics),
            "avg_gpu_utilization": sum(m.gpu_utilization for m in self.metrics) / len(self.metrics),
            "avg_response_time": sum(m.response_time for m in self.metrics) / len(self.metrics),
            "avg_tokens_per_second": sum(m.tokens_per_second for m in self.metrics) / len(self.metrics)
        }

# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # Simulate some work
    time.sleep(5)
    
    # Record inference
    monitor.record_inference(tokens=100, duration=1.5)
    
    # Get and print summary
    print(monitor.get_summary())
    
    monitor.stop_monitoring()
    monitor.save_metrics()
