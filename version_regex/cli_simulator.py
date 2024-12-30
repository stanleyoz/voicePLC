# cli_simulator.py

import cmd
import json
from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from device_components import Sensor, Actuator
from device import Device
from device_controller import DeviceController

console = Console()

class DeviceCommandSimulator(cmd.Cmd):
    intro = 'Welcome to the Device Control Simulator.\nType help or ? to list commands.\n'
    prompt = '(device-control) '

    def __init__(self, controller: DeviceController):
        console.print("[yellow]Initializing CLI simulator...[/yellow]")
        super().__init__()
        self.controller = controller
        self.history: list[Dict[str, Any]] = []
        console.print("[green]CLI simulator ready![/green]")

    def preloop(self):
        """Called before the command loop starts"""
        console.print("\n[bold blue]Starting command loop...[/bold blue]")

    def postloop(self):
        """Called when the command loop ends"""
        console.print("\n[yellow]Exiting simulator...[/yellow]")

    def do_command(self, arg: str):
        """
        Simulate a voice command
        Usage: command <natural language command>
        Example: command turn on the main pump in water system
        """
        if not arg:
            console.print("[red]Error: Please provide a command[/red]")
            return

        try:
            timestamp = datetime.now()
            command_record = {
                "timestamp": timestamp,
                "command": arg,
                "processed": None,
                "result": None
            }
            
            response = self.controller.process_command(arg)
            command_record["processed"] = True
            command_record["result"] = response
            self.history.append(command_record)
            self._display_command_result(command_record)

        except Exception as e:
            console.print(f"[red]Error processing command: {str(e)}[/red]")
            command_record = {
                "timestamp": timestamp,
                "command": arg,
                "processed": False,
                "result": str(e)
            }
            self.history.append(command_record)

    def do_status(self, arg: str):
        """
        Show current status of all devices or a specific device
        Usage: status [device_name]
        Example: status WaterSystem
        """
        if arg:
            device = self.controller.get_device(arg)
            if device:
                self._display_device_status(device)
            else:
                console.print(f"[red]Device '{arg}' not found[/red]")
        else:
            self._display_all_devices_status()

    def do_history(self, arg: str):
        """
        Show command history
        Usage: history [number of entries]
        """
        try:
            limit = int(arg) if arg else len(self.history)
        except ValueError:
            console.print("[red]Invalid number format[/red]")
            return

        table = Table(title="Command History")
        table.add_column("Time", style="cyan")
        table.add_column("Command", style="green")
        table.add_column("Status", style="magenta")
        table.add_column("Result", style="yellow")

        for record in self.history[-limit:]:
            timestamp = record["timestamp"].strftime("%H:%M:%S")
            status = "✓" if record["processed"] else "✗"
            result = str(record["result"])
            table.add_row(timestamp, record["command"], status, result)

        console.print(table)

    def do_quit(self, arg: str):
        """Exit the simulator"""
        return True

    def _display_command_result(self, record: Dict[str, Any]):
        """Display the result of a command in a formatted panel"""
        content = f"""
Command: {record['command']}
Time: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
Status: {'Success' if record['processed'] else 'Failed'}
Result: {record['result']}
        """
        console.print(Panel(content, title="Command Result", border_style="green"))

    def _display_device_status(self, device: Device):
        """Display detailed status for a single device"""
        table = Table(title=f"Device Status: {device.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        state = device.get_state()
        table.add_row("Name", state["name"])
        table.add_row("Site", state["site"])
        
        for name, status in state["actuators"].items():
            table.add_row(
                f"Actuator: {name}", 
                "ON" if status else "OFF"
            )
        
        for name, value in state["sensors"].items():
            sensor = device.get_sensor(name)
            if sensor and sensor.value is not None:
                table.add_row(
                    f"Sensor: {name}",
                    f"{sensor.value} {sensor.unit}"
                )
        
        console.print(table)

    def _display_all_devices_status(self):
        """Display status overview of all devices"""
        table = Table(title="All Devices Status")
        table.add_column("Device", style="cyan")
        table.add_column("Site", style="green")
        table.add_column("Actuators", style="yellow")
        table.add_column("Sensors", style="magenta")

        for name, device in self.controller.devices.items():
            state = device.get_state()
            actuators_status = ", ".join(
                f"{name}: {'ON' if status else 'OFF'}"
                for name, status in state["actuators"].items()
            )
            sensors_status = ", ".join(
                f"{name}: {value}"
                for name, value in state["sensors"].items()
            )
            
            table.add_row(
                name,
                state["site"],
                actuators_status or "None",
                sensors_status or "None"
            )

        console.print(table)
