# main.py

import argparse
from rich.console import Console
from device_controller import DeviceController
from device import Device
from device_components import FlowMeter, Pump, TemperatureSensor, Valve
from cli_simulator import DeviceCommandSimulator

console = Console()

def setup_mock_devices(controller: DeviceController) -> None:
    """Set up mock devices for testing"""
    console.print("[yellow]Setting up mock devices...[/yellow]")
    
    # Create a water system device
    water_system = Device("WaterSystem", "Building A")
    
    # Add actuators
    main_pump = Pump("MainPump", pin=18)
    backup_pump = Pump("BackupPump", pin=19)
    main_valve = Valve("MainValve", pin=20)
    
    water_system.add_actuator(main_pump)
    water_system.add_actuator(backup_pump)
    water_system.add_actuator(main_valve)
    
    # Add sensors
    flow_meter = FlowMeter("MainFlow", pin=21)
    temp_sensor = TemperatureSensor("WaterTemp", pin=22)
    
    water_system.add_sensor(flow_meter)
    water_system.add_sensor(temp_sensor)
    
    # Add device metadata
    water_system.set_metadata("description", "Primary water circulation system")
    water_system.set_metadata("location", "Mechanical Room 101")
    
    # Add device to controller
    controller.add_device(water_system)
    
    # Create a second device for testing
    hvac_system = Device("HVACSystem", "Building A")
    hvac_system.add_actuator(Pump("Circulator", pin=23))
    hvac_system.add_sensor(TemperatureSensor("ReturnTemp", pin=24))
    hvac_system.set_metadata("description", "HVAC circulation system")
    
    controller.add_device(hvac_system)
    console.print("[green]Mock devices setup complete![/green]")

def main():
    parser = argparse.ArgumentParser(description="Device Control System")
    parser.add_argument("--simulation", action="store_true", help="Run in simulation mode")
    parser.add_argument("--model", default="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                      help="Path to LLM model")
    parser.add_argument("--response-mode", choices=['llm', 'json'], default='llm',
                      help="Response mode: 'llm' for natural language, 'json' for raw data")
    args = parser.parse_args()
    
    try:
        # Initialize controller with model path and response mode
        console.print("[yellow]Initializing controller...[/yellow]")
        controller = DeviceController(
            model_path=args.model,
            llm_response=(args.response_mode == 'llm')
        )
        
        # Set up mock devices
        setup_mock_devices(controller)
        
        if args.simulation:
            # Run CLI simulator
            console.print("\n[bold green]=== Device Control System Simulator ===[/bold green]")
            console.print("[blue]Type 'help' or '?' to list commands.[/blue]")
            simulator = DeviceCommandSimulator(controller)
            simulator.cmdloop()
        else:
            # TODO: Implement voice control mode
            console.print("[red]Voice control mode not yet implemented[/red]")
            
    except KeyboardInterrupt:
        console.print("\nShutting down...")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise  # Re-raise the exception to see the full traceback
    finally:
        console.print("[green]Cleanup complete[/green]")

if __name__ == "__main__":
    main()
