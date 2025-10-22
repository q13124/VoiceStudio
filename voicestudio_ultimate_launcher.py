"""
VoiceStudio Ultimate Launcher
Unified launcher following the Unified Implementation Map
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import signal

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config.config_loader import get_config, Environment
from plugins.plugin_registry import get_plugin_registry
from security.security_manager import get_security_manager


class VoiceStudioLauncher:
    """Main VoiceStudio launcher"""

    def __init__(self):
        self.config = get_config()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        self.services = {
            "router": {
                "script": "workers/ops/voice_engine_router.py",
                "port": self.config.router.port,
                "name": "Voice Engine Router",
            },
            "gateway": {
                "script": "workers/ops/engine_gateway.py",
                "port": self.config.gateway.port,
                "name": "Engine Gateway",
            },
            "dashboard": {
                "script": "web/dashboard.html",
                "port": self.config.web_ui.port,
                "name": "Web Dashboard",
            },
        }

    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            print(f"Unknown service: {service_name}")
            return False

        service = self.services[service_name]
        script_path = Path(service["script"])

        if not script_path.exists():
            print(f"Service script not found: {script_path}")
            return False

        try:
            if service_name == "dashboard":
                # Start web server for dashboard
                self._start_web_server(service)
            else:
                # Start Python service
                self._start_python_service(service_name, service)

            print(f"✅ Started {service['name']} on port {service['port']}")
            return True

        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")
            return False

    def _start_python_service(self, service_name: str, service: Dict[str, Any]):
        """Start a Python service"""
        script_path = Path(service["script"])

        # Determine Python executable
        python_exe = self.config.gateway.python_exe
        if not Path(python_exe).exists():
            python_exe = sys.executable

        # Start the service
        process = subprocess.Popen(
            [python_exe, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent,
        )

        self.processes[service_name] = process

        # Start output monitoring thread
        threading.Thread(
            target=self._monitor_service_output,
            args=(service_name, process),
            daemon=True,
        ).start()

    def _start_web_server(self, service: Dict[str, Any]):
        """Start web server for dashboard"""
        import http.server
        import socketserver
        import threading

        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(
                    *args, directory=str(Path(__file__).parent / "web"), **kwargs
                )

        def run_server():
            with socketserver.TCPServer(
                ("", service["port"]), DashboardHandler
            ) as httpd:
                httpd.serve_forever()

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Store thread instead of process for web server
        self.processes["dashboard"] = server_thread

    def _monitor_service_output(self, service_name: str, process: subprocess.Popen):
        """Monitor service output"""
        try:
            for line in iter(process.stdout.readline, ""):
                if line:
                    print(f"[{service_name}] {line.strip()}")
        except Exception as e:
            print(f"Error monitoring {service_name}: {e}")

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.processes:
            print(f"Service {service_name} is not running")
            return False

        try:
            if service_name == "dashboard":
                # Web server thread will stop when main thread stops
                del self.processes[service_name]
            else:
                process = self.processes[service_name]
                process.terminate()
                process.wait(timeout=5)
                del self.processes[service_name]

            print(f"✅ Stopped {self.services[service_name]['name']}")
            return True

        except Exception as e:
            print(f"❌ Failed to stop {service_name}: {e}")
            return False

    def start_all_services(self) -> bool:
        """Start all services"""
        print("🚀 Starting VoiceStudio Ultimate...")
        print(f"Environment: {self.config.environment.value}")
        print(f"Router Port: {self.config.router.port}")
        print(f"Gateway Port: {self.config.gateway.port}")
        print(f"Dashboard Port: {self.config.web_ui.port}")
        print()

        success = True
        for service_name in self.services.keys():
            if not self.start_service(service_name):
                success = False

        if success:
            self.running = True
            print("✅ All services started successfully!")
            print()
            self._print_service_urls()
            print()
            print("Press Ctrl+C to stop all services")

        return success

    def stop_all_services(self):
        """Stop all services"""
        print("\n🛑 Stopping VoiceStudio services...")

        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

        self.running = False
        print("✅ All services stopped")

    def _print_service_urls(self):
        """Print service URLs"""
        print("📋 Service URLs:")
        print(f"  Router API: http://localhost:{self.config.router.port}")
        print(f"  Gateway API: http://localhost:{self.config.gateway.port}")
        print(f"  Web Dashboard: http://localhost:{self.config.web_ui.port}")
        print()
        print("🔗 Quick Links:")
        print(f"  Health Check: http://localhost:{self.config.router.port}/health")
        print(f"  Engine Status: http://localhost:{self.config.router.port}/engines")
        print(f"  Dashboard: http://localhost:{self.config.web_ui.port}/dashboard.html")

    def check_service_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        health_status = {}

        for service_name, service in self.services.items():
            try:
                import requests

                response = requests.get(
                    f"http://localhost:{service['port']}/health", timeout=2
                )
                health_status[service_name] = response.status_code == 200
            except:
                health_status[service_name] = False

        return health_status

    def run_interactive_mode(self):
        """Run in interactive mode"""
        print("🎤 VoiceStudio Ultimate - Interactive Mode")
        print("Commands: start, stop, restart, status, health, dashboard, quit")
        print()

        while True:
            try:
                command = input("VoiceStudio> ").strip().lower()

                if command == "quit" or command == "exit":
                    break
                elif command == "start":
                    self.start_all_services()
                elif command == "stop":
                    self.stop_all_services()
                elif command == "restart":
                    self.stop_all_services()
                    time.sleep(2)
                    self.start_all_services()
                elif command == "status":
                    self._print_status()
                elif command == "health":
                    self._print_health()
                elif command == "dashboard":
                    webbrowser.open(
                        f"http://localhost:{self.config.web_ui.port}/dashboard.html"
                    )
                elif command == "help":
                    print(
                        "Available commands: start, stop, restart, status, health, dashboard, quit"
                    )
                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        self.stop_all_services()

    def _print_status(self):
        """Print service status"""
        print("\n📊 Service Status:")
        for service_name, service in self.services.items():
            status = "Running" if service_name in self.processes else "Stopped"
            print(f"  {service['name']}: {status} (Port {service['port']})")
        print()

    def _print_health(self):
        """Print service health"""
        print("\n🏥 Service Health:")
        health_status = self.check_service_health()
        for service_name, service in self.services.items():
            health = (
                "Healthy" if health_status.get(service_name, False) else "Unhealthy"
            )
            print(f"  {service['name']}: {health}")
        print()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="VoiceStudio Ultimate Launcher")
    parser.add_argument(
        "--mode",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment mode",
    )
    parser.add_argument(
        "--services",
        default="router,gateway,dashboard",
        help="Comma-separated list of services to start",
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--health-check", action="store_true", help="Check service health and exit"
    )

    args = parser.parse_args()

    # Set environment
    os.environ["VOICESTUDIO_ENV"] = args.mode

    launcher = VoiceStudioLauncher()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down...")
        launcher.stop_all_services()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if args.health_check:
        health_status = launcher.check_service_health()
        for service, healthy in health_status.items():
            status = "✅" if healthy else "❌"
            print(f"{status} {service}")
        sys.exit(0 if all(health_status.values()) else 1)

    if args.interactive:
        launcher.run_interactive_mode()
    else:
        # Start specified services
        services_to_start = args.services.split(",")
        success = True

        for service in services_to_start:
            service = service.strip()
            if not launcher.start_service(service):
                success = False

        if success:
            launcher.running = True
            launcher._print_service_urls()

            # Keep running until interrupted
            try:
                while launcher.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        launcher.stop_all_services()


if __name__ == "__main__":
    main()
