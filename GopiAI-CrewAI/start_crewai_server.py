import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None, shell=False):
    print(f"Executing: {' '.join(command) if isinstance(command, list) else command}")
    result = subprocess.run(command, cwd=cwd, shell=shell, capture_output=True, text=True, encoding='utf-8')
    if result.stdout:
        print(f"Stdout:\n{result.stdout}")
    if result.stderr:
        print(f"Stderr:\n{result.stderr}")
    result.check_returncode()
    return result

def main():
    current_dir = Path(__file__).parent.absolute()
    venv_dir = current_dir / "crewai_env"
    python_executable = venv_dir / "Scripts" / "python.exe" if sys.platform == "win32" else venv_dir / "bin" / "python"
    pip_executable = venv_dir / "Scripts" / "pip.exe" if sys.platform == "win32" else venv_dir / "bin" / "pip"
    
    # 1. Check and create virtual environment
    if not venv_dir.exists():
        print("[1/4] Creating CrewAI virtual environment...")
        run_command([sys.executable, "-m", "venv", str(venv_dir)])
    else:
        print("[1/4] Virtual environment already exists.")

    # 2. Activate virtual environment (for setting up environment variables for subprocess)
    # This is more about setting up the correct python for subsequent commands
    print("[2/4] Activating CrewAI environment...")
    # For Windows, activate.bat sets VIRTUAL_ENV and modifies PATH
    # For Python, we directly use the venv's python executable
    
    # 3. Install dependencies
    print("[3/4] Checking and installing dependencies...")
    requirements_path = current_dir / "requirements.txt"
    if requirements_path.exists():
        run_command([str(pip_executable), "install", "-r", str(requirements_path)])
    else:
        print("Warning: requirements.txt not found. Skipping dependency installation.")

    # Set PYTHONPATH for correct module imports
    # This is crucial for the server to find its modules
    os.environ["PYTHONPATH"] = str(venv_dir / "Lib" / "site-packages") + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONIOENCODING"] = "UTF-8"

    # 4. Run the debug wrapper
    print("[4/4] Starting CrewAI API server...")
    debug_wrapper_path = current_dir / "debug_wrapper.py"
    run_command([str(python_executable), str(debug_wrapper_path)])

if __name__ == "__main__":
    main()
