#!/usr/bin/env python3
# test_dependencies.py

import sys
import subprocess
from typing import Dict, Callable, Any
from rich.console import Console
from rich.table import Table

console = Console()

def get_package_version(package: str) -> str:
    """Get package version using pip"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('Version: '):
                return line.split('Version: ')[1]
    except Exception:
        return "Not Found"
    return "Unknown"

def test_dependencies():
    # Define tests for each package with minimum versions
    tests: Dict[str, Dict[str, Any]] = {
        'Python': {
            'test': lambda: sys.version_info >= (3, 10),
            'version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'required': "3.10+"
        },
        'PyTorch': {
            'test': lambda: __import__('torch'),
            'version': lambda: get_package_version('torch'),
            'required': "Any"
        },
        'Rich': {
            'test': lambda: __import__('rich'),
            'version': lambda: get_package_version('rich'),
            'required': "Any"
        },
        'Vosk': {
            'test': lambda: __import__('vosk'),
            'version': lambda: get_package_version('vosk'),
            'required': "0.3.45"
        },
        'Sounddevice': {
            'test': lambda: __import__('sounddevice'),
            'version': lambda: get_package_version('sounddevice'),
            'required': "Any"
        },
        'Transformers': {
            'test': lambda: __import__('transformers'),
            'version': lambda: get_package_version('transformers'),
            'required': "Any"
        },
        'Optimum': {
            'test': lambda: __import__('optimum'),
            'version': lambda: get_package_version('optimum'),
            'required': "Any"
        },
        'Auto-GPTQ': {
            'test': lambda: __import__('auto_gptq'),
            'version': lambda: get_package_version('auto-gptq'),
            'required': "Any"
        },
        'Llama-cpp-python': {
            'test': lambda: __import__('llama_cpp'),
            'version': lambda: get_package_version('llama-cpp-python'),
            'required': "Any"
        },
        'NumPy': {
            'test': lambda: __import__('numpy'),
            'version': lambda: get_package_version('numpy'),
            'required': "Any"
        },
        'PortAudio': {
            'test': lambda: __import__('pyaudio'),
            'version': lambda: get_package_version('pyaudio'),
            'required': "Any"
        }
    }

    # Create results table
    table = Table(title="Dependency Test Results")
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Required Version", style="yellow")
    table.add_column("Installed Version", style="blue")
    table.add_column("Notes", style="magenta")

    all_passed = True
    
    # Test each dependency
    for package_name, package_info in tests.items():
        try:
            # Run the test
            package_info['test']()
            
            # Get version
            version = package_info['version']() if callable(package_info['version']) else package_info['version']
            
            status = "✅ Pass"
            notes = ""
            
        except Exception as e:
            status = "❌ Fail"
            version = "Not Installed"
            notes = str(e)
            all_passed = False

        table.add_row(
            package_name,
            status,
            package_info['required'],
            version,
            notes
        )

    # Display results
    console.print("\n=== Device Control System Dependency Test ===\n")
    console.print(table)
    
    # Print system info
    console.print("\n=== System Information ===")
    console.print(f"Python Path: {sys.executable}")
    console.print(f"Platform: {sys.platform}")
    
    # Print conda environment if available
    try:
        conda_env = subprocess.run(['conda', 'info'], capture_output=True, text=True)
        if conda_env.returncode == 0:
            console.print("\n=== Conda Environment ===")
            console.print(conda_env.stdout)
    except FileNotFoundError:
        console.print("\nConda not found in PATH")

    # Final summary
    if all_passed:
        console.print("\n[green]All dependencies are properly installed![/green]")
    else:
        console.print("\n[red]Some dependencies are missing or failed to load.[/red]")
        console.print("\nTo install missing dependencies:")
        console.print("""
1. Ensure conda environment is activated:
   conda activate device_control

2. Install required packages:
   conda install -c conda-forge numpy
   conda install -c pytorch pytorch cpuonly
   conda install -c conda-forge rich
   conda install -c conda-forge portaudio
   pip install sounddevice
   pip install vosk==0.3.45
   pip install transformers optimum auto-gptq
   pip install llama-cpp-python
        """)

if __name__ == "__main__":
    test_dependencies()
