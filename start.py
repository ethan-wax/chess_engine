#!/usr/bin/env python3
"""
Chess Engine Development Startup Script
This script starts both the backend (FastAPI) and frontend (React + Vite) servers
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def check_command_exists(command):
    """Check if a command exists in PATH"""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_port_in_use(port):
    """Check if a port is in use (both IPv4 and IPv6)"""
    import socket
    try:
        # Check IPv4
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                return True
        
        # Check IPv6
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('::1', port))
            if result == 0:
                return True
        
        return False
    except Exception:
        return False

def kill_port_processes(port):
    """Kill processes using a specific port"""
    try:
        if sys.platform == "win32":
            # Windows implementation
            subprocess.run(['netstat', '-ano'], capture_output=True)
        else:
            # Unix-like systems
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(['kill', '-9', pid], check=True)
                    except subprocess.CalledProcessError:
                        pass
    except Exception:
        pass

class ServerManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.script_dir = Path(__file__).parent.absolute()
        self.backend_dir = self.script_dir / "backend"
        self.frontend_dir = self.script_dir / "frontend"
        
    def check_prerequisites(self):
        """Check if required tools are installed"""
        print_status("Checking prerequisites...")
        
        if not check_command_exists('uv'):
            print_error("uv is not installed. Please install it first:")
            print("curl -LsSf https://astral.sh/uv/install.sh | sh")
            return False
            
        if not check_command_exists('node'):
            print_error("Node.js is not installed. Please install it first:")
            print("Visit: https://nodejs.org/")
            return False
            
        if not check_command_exists('npm'):
            print_error("npm is not installed. Please install it first.")
            return False
            
        print_success("All prerequisites are installed")
        return True
    
    def start_backend(self):
        """Start the backend server"""
        print_status("Starting backend server...")
        
        if not self.backend_dir.exists():
            print_error(f"Backend directory not found: {self.backend_dir}")
            return False
            
        os.chdir(self.backend_dir)
        
        # Install dependencies if needed
        if not (self.backend_dir / ".venv").exists():
            print_status("Installing backend dependencies...")
            try:
                subprocess.run(['uv', 'sync'], check=True)
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install backend dependencies: {e}")
                return False
        
        # Start the FastAPI server
        print_status("Starting FastAPI server on http://localhost:8000")
        try:
            self.backend_process = subprocess.Popen([
                'uv', 'run', 'uvicorn', 'main:app', 
                '--host', '0.0.0.0', '--port', '8000', '--reload'
            ])
            return True
        except Exception as e:
            print_error(f"Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        print_status("Starting frontend server...")
        
        if not self.frontend_dir.exists():
            print_error(f"Frontend directory not found: {self.frontend_dir}")
            return False
            
        os.chdir(self.frontend_dir)
        
        # Install dependencies if needed
        if not (self.frontend_dir / "node_modules").exists():
            print_status("Installing frontend dependencies...")
            try:
                subprocess.run(['npm', 'install'], check=True)
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install frontend dependencies: {e}")
                return False
        
        # Start the Vite dev server
        print_status("Starting Vite dev server on http://localhost:5173")
        try:
            self.frontend_process = subprocess.Popen(['npm', 'run', 'dev'])
            return True
        except Exception as e:
            print_error(f"Failed to start frontend: {e}")
            return False
    
    def cleanup(self):
        """Clean up running processes"""
        print_status("Shutting down servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print_success("Backend server stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print_warning("Backend server force killed")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                print_success("Frontend server stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print_warning("Frontend server force killed")
        
        # Kill any remaining processes on our ports
        kill_port_processes(8000)
        kill_port_processes(5173)
        
        print_success("Cleanup complete")
    
    def wait_for_server(self, process, port, name, timeout=15):
        """Wait for a server to start and verify it's running"""
        print_status(f"Waiting for {name} to start...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if process is still running
            if process.poll() is not None:
                print_error(f"{name} process exited unexpectedly")
                return False
            
            # Check if port is in use
            if is_port_in_use(port):
                print_success(f"{name} is running on http://localhost:{port}")
                return True
            
            time.sleep(1)
        
        print_error(f"{name} failed to start within {timeout} seconds")
        return False
    
    def run(self):
        """Main run method"""
        if not self.check_prerequisites():
            return 1
        
        # Kill any existing processes on our ports
        print_status("Freeing up ports 8000 and 5173...")
        kill_port_processes(8000)
        kill_port_processes(5173)
        
        # Start backend
        if not self.start_backend():
            return 1
        
        # Wait for backend to start
        if not self.wait_for_server(self.backend_process, 8000, "Backend server"):
            self.cleanup()
            return 1
        
        # Start frontend
        if not self.start_frontend():
            self.cleanup()
            return 1
        
        # Wait for frontend to start
        if not self.wait_for_server(self.frontend_process, 5173, "Frontend server"):
            self.cleanup()
            return 1
        
        print_success("Both servers are running successfully!")
        print("")
        print(f"{Colors.GREEN}🚀 Chess Engine Development Environment{Colors.NC}")
        print(f"{Colors.BLUE}Backend API:{Colors.NC} http://localhost:8000")
        print(f"{Colors.BLUE}Frontend App:{Colors.NC} http://localhost:5173")
        print(f"{Colors.BLUE}API Docs:{Colors.NC} http://localhost:8000/docs")
        print("")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop both servers{Colors.NC}")
        
        try:
            # Wait for processes
            while True:
                # Check if either process has died
                if self.backend_process and self.backend_process.poll() is not None:
                    print_error("Backend server stopped unexpectedly")
                    break
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print_error("Frontend server stopped unexpectedly")
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return 0

def main():
    """Main entry point"""
    manager = ServerManager()
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return manager.run()

if __name__ == "__main__":
    sys.exit(main())