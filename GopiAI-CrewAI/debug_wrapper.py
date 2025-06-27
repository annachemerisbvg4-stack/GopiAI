#!/usr/bin/env python3
"""
Debug Wrapper for CrewAI API Server
Launches the server in a fault-tolerant mode with error interception
"""

import os
import sys
import traceback
import time
import subprocess
from pathlib import Path

def run_server_with_retry():
    """Запускает сервер с автоматическим перезапуском при сбое"""
    
    max_retries = 3
    retry_count = 0
    retry_delay = 5  # секунд
    
    print("=" * 60)
    print("DEBUG WRAPPER for CrewAI API Server")
    print("=" * 60)
    print("This script launches the server with automatic restart on failure")
    print()
    
    # Get the path to the current script directory
    current_dir = Path(__file__).parent.absolute()
    server_path = current_dir / "crewai_api_server.py"
    
    while retry_count < max_retries:
        try:
            print(f"Attempting to start server ({retry_count + 1}/{max_retries})...")
            
            # Use subprocess to launch the server in a separate process
            process = subprocess.Popen(
                [sys.executable, str(server_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True, # Use text mode for universal newlines and encoding
                encoding='utf-8' # Explicitly set encoding for subprocess communication
            )
            
            # Wait for the process to complete and get the output
            stdout, stderr = process.communicate()
            
            if stdout:
                print("Server Stdout:")
                print(stdout)
            if stderr:
                print("Server Stderr:")
                print(stderr)
            
            # If the process exited with an error
            if process.returncode != 0:
                print("Сервер завершился с кодом {process.returncode}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Превышено максимальное количество попыток")
            else:
                # Normal termination
                print("Server finished without errors")
                break
                
        except KeyboardInterrupt:
            print("Operation interrupted by user")
            break
        except Exception as e:
            print(f"Error starting server: {e}")
            traceback.print_exc()
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum number of retries exceeded")
    
    print("[DEBUG WRAPPER] Exiting.")

if __name__ == "__main__":
    run_server_with_retry()