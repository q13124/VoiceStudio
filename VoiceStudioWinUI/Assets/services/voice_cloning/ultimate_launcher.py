#!/usr/bin/env python3
"""
VoiceStudio Ultimate Voice Cloning Launcher
Main launcher for all voice cloning services
Version: 3.0.0 "Ultimate Launcher"
"""

import asyncio
import logging
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import argparse
import subprocess
import threading
import multiprocessing as mp
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("voicestudio_ultimate.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class VoiceStudioUltimateLauncher:
    """Ultimate launcher for VoiceStudio voice cloning services"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Service status
        self.services = {
            "ultimate_engine": {
                "name": "Ultimate Voice Cloning Engine",
                "status": "stopped",
                "process": None,
                "port": 8080,
                "enabled": True,
            },
            "real_time_engine": {
                "name": "Real-Time Voice Cloning Engine",
                "status": "stopped",
                "process": None,
                "port": 8081,
                "enabled": True,
            },
            "performance_optimizer": {
                "name": "Performance Optimizer",
                "status": "stopped",
                "process": None,
                "port": None,
                "enabled": True,
            },
            "upgrade_system": {
                "name": "Upgrade System",
                "status": "stopped",
                "process": None,
                "port": None,
                "enabled": True,
            },
            "web_server": {
                "name": "Ultimate Web Server",
                "status": "stopped",
                "process": None,
                "port": 8082,
                "enabled": True,
            },
        }

        # System status
        self.system_active = False
        self.start_time = None

        # Configuration
        self.config = {
            "auto_start_services": True,
            "monitor_services": True,
            "restart_on_failure": True,
            "log_level": "INFO",
            "max_restart_attempts": 3,
        }

    async def start_all_services(self):
        """Start all VoiceStudio voice cloning services"""
        try:
            self.logger.info("Starting VoiceStudio Ultimate Voice Cloning Services")

            self.system_active = True
            self.start_time = datetime.now()

            # Start services in order
            services_to_start = [
                ("performance_optimizer", self._start_performance_optimizer),
                ("upgrade_system", self._start_upgrade_system),
                ("ultimate_engine", self._start_ultimate_engine),
                ("real_time_engine", self._start_real_time_engine),
                ("web_server", self._start_web_server),
            ]

            for service_id, start_func in services_to_start:
                if self.services[service_id]["enabled"]:
                    try:
                        await start_func(service_id)
                        self.logger.info(
                            f"✅ {self.services[service_id]['name']} started successfully"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"❌ Failed to start {self.services[service_id]['name']}: {e}"
                        )
                        if self.config["restart_on_failure"]:
                            await self._restart_service(service_id)

            # Start monitoring
            if self.config["monitor_services"]:
                asyncio.create_task(self._monitor_services())

            self.logger.info(
                "VoiceStudio Ultimate Voice Cloning Services started successfully"
            )

        except Exception as e:
            self.logger.error(f"Failed to start services: {e}")
            raise

    async def _start_performance_optimizer(self, service_id: str):
        """Start performance optimizer service"""
        try:
            script_path = Path(
                "services/voice_cloning/performance_optimizer_ultimate.py"
            )
            if not script_path.exists():
                self.logger.warning(
                    f"Performance optimizer script not found: {script_path}"
                )
                return

            # Start performance optimizer
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.services[service_id]["process"] = process
            self.services[service_id]["status"] = "running"

        except Exception as e:
            self.logger.error(f"Failed to start performance optimizer: {e}")
            raise

    async def _start_upgrade_system(self, service_id: str):
        """Start upgrade system service"""
        try:
            script_path = Path("services/voice_cloning/ultimate_upgrade_system.py")
            if not script_path.exists():
                self.logger.warning(f"Upgrade system script not found: {script_path}")
                return

            # Start upgrade system
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.services[service_id]["process"] = process
            self.services[service_id]["status"] = "running"

        except Exception as e:
            self.logger.error(f"Failed to start upgrade system: {e}")
            raise

    async def _start_ultimate_engine(self, service_id: str):
        """Start ultimate voice cloning engine"""
        try:
            script_path = Path(
                "services/voice_cloning/ultimate_voice_cloning_engine.py"
            )
            if not script_path.exists():
                self.logger.warning(f"Ultimate engine script not found: {script_path}")
                return

            # Start ultimate engine
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.services[service_id]["process"] = process
            self.services[service_id]["status"] = "running"

        except Exception as e:
            self.logger.error(f"Failed to start ultimate engine: {e}")
            raise

    async def _start_real_time_engine(self, service_id: str):
        """Start real-time voice cloning engine"""
        try:
            script_path = Path(
                "services/voice_cloning/real_time_voice_cloning_system.py"
            )
            if not script_path.exists():
                self.logger.warning(f"Real-time engine script not found: {script_path}")
                return

            # Start real-time engine
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.services[service_id]["process"] = process
            self.services[service_id]["status"] = "running"

        except Exception as e:
            self.logger.error(f"Failed to start real-time engine: {e}")
            raise

    async def _start_web_server(self, service_id: str):
        """Start ultimate web server"""
        try:
            script_path = Path("services/voice_cloning/ultimate_web_server.py")
            if not script_path.exists():
                self.logger.warning(f"Web server script not found: {script_path}")
                return

            # Start web server
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.services[service_id]["process"] = process
            self.services[service_id]["status"] = "running"

        except Exception as e:
            self.logger.error(f"Failed to start web server: {e}")
            raise

    async def _restart_service(self, service_id: str):
        """Restart a failed service"""
        try:
            service = self.services[service_id]
            self.logger.info(f"Restarting {service['name']}...")

            # Stop current process
            if service["process"]:
                service["process"].terminate()
                await service["process"].wait()

            # Start service again
            start_funcs = {
                "performance_optimizer": self._start_performance_optimizer,
                "upgrade_system": self._start_upgrade_system,
                "ultimate_engine": self._start_ultimate_engine,
                "real_time_engine": self._start_real_time_engine,
                "web_server": self._start_web_server,
            }

            if service_id in start_funcs:
                await start_funcs[service_id](service_id)
                self.logger.info(f"✅ {service['name']} restarted successfully")

        except Exception as e:
            self.logger.error(f"Failed to restart {service_id}: {e}")

    async def _monitor_services(self):
        """Monitor all services"""
        try:
            while self.system_active:
                for service_id, service in self.services.items():
                    if service["enabled"] and service["process"]:
                        # Check if process is still running
                        if service["process"].returncode is not None:
                            self.logger.warning(
                                f"Service {service['name']} stopped unexpectedly"
                            )
                            service["status"] = "stopped"

                            if self.config["restart_on_failure"]:
                                await self._restart_service(service_id)

                await asyncio.sleep(10)  # Check every 10 seconds

        except Exception as e:
            self.logger.error(f"Service monitoring failed: {e}")

    async def stop_all_services(self):
        """Stop all VoiceStudio voice cloning services"""
        try:
            self.logger.info("Stopping VoiceStudio Ultimate Voice Cloning Services")

            self.system_active = False

            # Stop all services
            for service_id, service in self.services.items():
                if service["process"]:
                    try:
                        service["process"].terminate()
                        await service["process"].wait()
                        service["status"] = "stopped"
                        self.logger.info(f"✅ {service['name']} stopped successfully")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to stop {service['name']}: {e}")

            self.logger.info("VoiceStudio Ultimate Voice Cloning Services stopped")

        except Exception as e:
            self.logger.error(f"Failed to stop services: {e}")
            raise

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "system_active": self.system_active,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "uptime": (
                    (datetime.now() - self.start_time).total_seconds()
                    if self.start_time
                    else 0
                ),
                "services": {
                    service_id: {
                        "name": service["name"],
                        "status": service["status"],
                        "enabled": service["enabled"],
                        "port": service["port"],
                    }
                    for service_id, service in self.services.items()
                },
                "system_info": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": (
                        psutil.disk_usage("/").percent
                        if os.name != "nt"
                        else psutil.disk_usage("C:").percent
                    ),
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}

    def print_status(self):
        """Print system status"""
        try:
            status = self.get_system_status()

            print("\n" + "=" * 80)
            print("  VOICESTUDIO ULTIMATE VOICE CLONING SYSTEM STATUS")
            print("=" * 80)
            print(
                f"  System Active: {'✅ YES' if status['system_active'] else '❌ NO'}"
            )
            print(f"  Start Time: {status['start_time']}")
            print(f"  Uptime: {status['uptime']:.1f} seconds")
            print()
            print("  SERVICES:")
            for service_id, service_info in status["services"].items():
                status_icon = "✅" if service_info["status"] == "running" else "❌"
                port_info = (
                    f" (Port: {service_info['port']})" if service_info["port"] else ""
                )
                print(f"    {status_icon} {service_info['name']}{port_info}")
            print()
            print("  SYSTEM RESOURCES:")
            print(f"    CPU Usage: {status['system_info']['cpu_percent']:.1f}%")
            print(f"    Memory Usage: {status['system_info']['memory_percent']:.1f}%")
            print(f"    Disk Usage: {status['system_info']['disk_percent']:.1f}%")
            print("=" * 80)

        except Exception as e:
            self.logger.error(f"Failed to print status: {e}")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="VoiceStudio Ultimate Voice Cloning Launcher"
    )
    parser.add_argument("--start", action="store_true", help="Start all services")
    parser.add_argument("--stop", action="store_true", help="Stop all services")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    # Initialize launcher
    launcher = VoiceStudioUltimateLauncher()

    try:
        if args.start:
            print("Starting VoiceStudio Ultimate Voice Cloning Services...")
            await launcher.start_all_services()

            if args.daemon:
                print("Running as daemon. Press Ctrl+C to stop.")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\nStopping services...")
                    await launcher.stop_all_services()
            else:
                print("Services started. Press Enter to stop.")
                input()
                await launcher.stop_all_services()

        elif args.stop:
            print("Stopping VoiceStudio Ultimate Voice Cloning Services...")
            await launcher.stop_all_services()

        elif args.status:
            launcher.print_status()

        else:
            print("VoiceStudio Ultimate Voice Cloning Launcher")
            print("Use --help for available options")

    except Exception as e:
        logger.error(f"Launcher failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
