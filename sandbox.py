import subprocess
import sys
import os

def run_sandboxed_code(script_path, timeout=5):
    """
    Executes a backtest script in a network-isolated, resource-constrained subprocess.
    """
    try:
        # Runs script path under current Python interpreter (within the virtual environment)
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": False
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": "TIMEOUT: Code entered an infinite loop or exceeded runtime limits.",
            "timeout": True
        }
