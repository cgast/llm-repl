#!/usr/bin/env python3
"""
Start script for the LLM-REPL Web UI.

This script starts both the backend Flask server and the frontend React development server.
"""

import os
import sys
import subprocess
import time
import webbrowser
import signal
import atexit
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Start the LLM-REPL Web UI')
parser.add_argument('--backend-host', default=os.environ.get('BACKEND_HOST', 'localhost'),
                    help='Backend host (default: localhost)')
parser.add_argument('--backend-port', type=int, default=int(os.environ.get('BACKEND_PORT', '5000')),
                    help='Backend port (default: 5000)')
parser.add_argument('--frontend-host', default=os.environ.get('FRONTEND_HOST', 'localhost'),
                    help='Frontend host (default: localhost)')
parser.add_argument('--frontend-port', type=int, default=int(os.environ.get('FRONTEND_PORT', '8081')),
                    help='Frontend port (default: 8081)')
parser.add_argument('--no-browser', action='store_true',
                    help='Do not open the browser automatically')
args = parser.parse_args()

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, 'backend')
FRONTEND_DIR = os.path.join(SCRIPT_DIR, 'frontend')

# Define commands
BACKEND_CMD = ['python', 'app.py', '--host', args.backend_host, '--port', str(args.backend_port)]
FRONTEND_CMD = ['npm', 'start']
FRONTEND_ENV = {
    'PORT': str(args.frontend_port),
    'REACT_APP_API_BASE_URL': f'http://{args.backend_host}:{args.backend_port}',
    'REACT_APP_SOCKET_URL': f'http://{args.backend_host}:{args.backend_port}'
}

# Define URLs
BACKEND_URL = f'http://{args.backend_host}:{args.backend_port}'
FRONTEND_URL = f'http://{args.frontend_host}:{args.frontend_port}'

# Define processes
backend_process = None
frontend_process = None


def start_backend():
    """Start the backend Flask server."""
    global backend_process
    print("Starting backend server...")
    backend_process = subprocess.Popen(
        BACKEND_CMD,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # Capture stderr separately
        universal_newlines=True,
        bufsize=1
    )
    
    # Wait for the backend to start
    print("Waiting for backend server to start...")
    time.sleep(2)
    
    # Check if the backend is running
    try:
        import requests
        response = requests.get(f"{BACKEND_URL}/api/notebooks")
        if response.status_code == 200:
            print(f"Backend server is running at {BACKEND_URL}")
        else:
            print(f"Backend server returned status code {response.status_code}")
    except Exception as e:
        print(f"Error connecting to backend server: {e}")


def start_frontend():
    """Start the frontend React development server."""
    global frontend_process
    print("Starting frontend server...")
    env = os.environ.copy()
    env.update(FRONTEND_ENV)
    print(f"Frontend environment variables: PORT={env.get('PORT')}, REACT_APP_API_BASE_URL={env.get('REACT_APP_API_BASE_URL')}, REACT_APP_SOCKET_URL={env.get('REACT_APP_SOCKET_URL')}")
    frontend_process = subprocess.Popen(
        FRONTEND_CMD,
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # Capture stderr separately
        universal_newlines=True,
        bufsize=1,
        env=env
    )
    
    # Wait for the frontend to start
    print("Waiting for frontend server to start...")
    time.sleep(5)
    
    # Check if the frontend process is still running
    if frontend_process.poll() is not None:
        print(f"Frontend process exited with code {frontend_process.returncode}")
        # Print any output from the frontend
        stdout, stderr = frontend_process.communicate()
        print("Frontend stdout:")
        print(stdout)
        print("Frontend stderr:")
        print(stderr)
        return
    
    # Open the frontend in the default browser if not disabled
    if not args.no_browser:
        print(f"Opening {FRONTEND_URL} in the default browser...")
        webbrowser.open(FRONTEND_URL)
    else:
        print(f"Frontend available at {FRONTEND_URL}")


def cleanup():
    """Clean up processes on exit."""
    if backend_process:
        print("Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()
    
    if frontend_process:
        print("Stopping frontend server...")
        frontend_process.terminate()
        frontend_process.wait()


def signal_handler(sig, frame):
    """Handle signals."""
    print("Received signal to terminate...")
    cleanup()
    sys.exit(0)


def main():
    """Main function."""
    # Register cleanup function
    atexit.register(cleanup)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the backend server
    start_backend()
    
    # Start the frontend server
    start_frontend()
    
    # Monitor the processes
    print("Monitoring processes...")
    try:
        while True:
            # Check if the backend is still running
            if backend_process and backend_process.poll() is not None:
                print("Backend server has stopped.")
                break
            
            # Check if the frontend is still running
            if frontend_process and frontend_process.poll() is not None:
                print("Frontend server has stopped.")
                break
            
            # Print output from the backend
            if backend_process and backend_process.stdout:
                while True:
                    line = backend_process.stdout.readline()
                    if not line:
                        break
                    print(f"[Backend] {line.strip()}")
            
            # Print stderr from the backend
            if backend_process and backend_process.stderr:
                while True:
                    line = backend_process.stderr.readline()
                    if not line:
                        break
                    print(f"[Backend ERROR] {line.strip()}")
            
            # Print output from the frontend
            if frontend_process and frontend_process.stdout:
                while True:
                    line = frontend_process.stdout.readline()
                    if not line:
                        break
                    print(f"[Frontend] {line.strip()}")
            
            # Print stderr from the frontend
            if frontend_process and frontend_process.stderr:
                while True:
                    line = frontend_process.stderr.readline()
                    if not line:
                        break
                    print(f"[Frontend ERROR] {line.strip()}")
            
            # Sleep for a bit
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received.")
    finally:
        cleanup()


if __name__ == '__main__':
    main()
