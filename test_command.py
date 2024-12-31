# test_command.py
from device_controller import DeviceController
from rich.console import Console

console = Console()

def main():
    # Initialize controller with mock devices
    controller = DeviceController(
        model_path="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        mock=True
    )
    
    print("Command processing test (type 'quit' to exit)")
    print("Example commands:")
    print("- What is the temperature of sensor_1?")
    print("- Turn actuator_1 on")
    print("- Get status of all devices")
    
    while True:
        try:
            command = input("\nEnter command: ")
            if command.lower() == 'quit':
                break
                
            # Process command and get response
            response = controller.process_command(command)
            console.print(f"[green]Response:[/green] {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")

if __name__ == "__main__":
    main()
