#!/usr/bin/env python3
"""
VoiceStudio Ultimate Launcher
Main application launcher with GUI and service management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import os
import sys
import json
import webbrowser
from pathlib import Path
import psutil

class VoiceStudioLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VoiceStudio Ultimate")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set window icon
        try:
            self.root.iconbitmap("voicestudio.ico")
        except:
            pass
        
        self.services = {
            "assistant": {"name": "Assistant Service", "port": 5080, "running": False, "url": "http://127.0.0.1:5080"},
            "voice_cloning": {"name": "Voice Cloning Service", "port": 5081, "running": False, "url": "http://127.0.0.1:5081"},
            "orchestrator": {"name": "Service Orchestrator", "port": 5082, "running": False, "url": "http://127.0.0.1:5082"}
        }
        
        self.create_ui()
        self.check_services()
        
    def create_ui(self):
        """Create user interface"""
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="VoiceStudio Ultimate", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Advanced Voice Cloning & AI Assistant System", 
                                  font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 30))
        
        # Service status frame
        status_frame = ttk.LabelFrame(main_frame, text="Service Status", padding="15")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        status_frame.columnconfigure(1, weight=1)
        
        self.service_vars = {}
        self.service_labels = {}
        
        for i, (service_id, service_info) in enumerate(self.services.items()):
            # Service name
            name_label = ttk.Label(status_frame, text=service_info["name"], 
                                 font=("Arial", 10, "bold"))
            name_label.grid(row=i, column=0, sticky=tk.W, pady=5)
            
            # Status indicator
            status_label = ttk.Label(status_frame, text="Checking...", foreground="orange")
            status_label.grid(row=i, column=1, sticky=tk.W, padx=(20, 0), pady=5)
            self.service_labels[service_id] = status_label
            
            # Open button
            open_btn = ttk.Button(status_frame, text="Open", 
                               command=lambda sid=service_id: self.open_service(sid))
            open_btn.grid(row=i, column=2, padx=(10, 0), pady=5)
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Service Control", padding="15")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, columnspan=3)
        
        ttk.Button(button_frame, text="Start All Services", 
                  command=self.start_all_services).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Stop All Services", 
                  command=self.stop_all_services).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Restart All Services", 
                  command=self.restart_all_services).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Check Status", 
                  command=self.check_services).grid(row=0, column=3, padx=5, pady=5)
        
        # Applications frame
        app_frame = ttk.LabelFrame(main_frame, text="Applications", padding="15")
        app_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        app_button_frame = ttk.Frame(app_frame)
        app_button_frame.grid(row=0, column=0, columnspan=3)
        
        ttk.Button(app_button_frame, text="VoiceStudio Assistant", 
                  command=self.open_assistant).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(app_button_frame, text="Voice Cloning Studio", 
                  command=self.open_voice_cloner).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(app_button_frame, text="Service Dashboard", 
                  command=self.open_dashboard).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(app_button_frame, text="System Monitor", 
                  command=self.open_monitor).grid(row=0, column=3, padx=5, pady=5)
        
        # System info frame
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="15")
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = tk.Text(info_frame, height=10, width=80, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        # Update system info
        self.update_system_info()
        
    def check_services(self):
        """Check service status"""
        for service_id, service_info in self.services.items():
            try:
                # Check if port is in use
                running = False
                for conn in psutil.net_connections():
                    if conn.laddr.port == service_info["port"] and conn.status == "LISTEN":
                        running = True
                        break
                
                service_info["running"] = running
                
                if running:
                    self.service_labels[service_id].config(text="Running", foreground="green")
                else:
                    self.service_labels[service_id].config(text="Stopped", foreground="red")
                    
            except Exception as e:
                service_info["running"] = False
                self.service_labels[service_id].config(text="Error", foreground="orange")
        
        # Schedule next check
        self.root.after(5000, self.check_services)
    
    def start_all_services(self):
        """Start all services"""
        def start_services():
            for service_id, service_info in self.services.items():
                try:
                    if not service_info["running"]:
                        # Start service based on type
                        if service_id == "assistant":
                            subprocess.Popen([sys.executable, "services/assistant/enhanced_service.py"], 
                                          cwd=os.path.dirname(__file__))
                        elif service_id == "voice_cloning":
                            subprocess.Popen([sys.executable, "services/voice_cloning/voice_cloning_service.py"], 
                                          cwd=os.path.dirname(__file__))
                        elif service_id == "orchestrator":
                            subprocess.Popen([sys.executable, "services/service_orchestrator.py"], 
                                          cwd=os.path.dirname(__file__))
                        
                        time.sleep(2)
                        self.service_labels[service_id].config(text="Starting...", foreground="orange")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to start {service_info['name']}: {e}")
        
        threading.Thread(target=start_services, daemon=True).start()
    
    def stop_all_services(self):
        """Stop all services"""
        def stop_services():
            for service_id, service_info in self.services.items():
                try:
                    if service_info["running"]:
                        # Find and kill processes using the ports
                        for conn in psutil.net_connections():
                            if conn.laddr.port == service_info["port"] and conn.status == "LISTEN":
                                try:
                                    process = psutil.Process(conn.pid)
                                    process.terminate()
                                    process.wait(timeout=5)
                                except:
                                    pass
                        
                        self.service_labels[service_id].config(text="Stopping...", foreground="orange")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to stop {service_info['name']}: {e}")
        
        threading.Thread(target=stop_services, daemon=True).start()
    
    def restart_all_services(self):
        """Restart all services"""
        self.stop_all_services()
        time.sleep(3)
        self.start_all_services()
    
    def open_service(self, service_id):
        """Open a specific service"""
        service_info = self.services[service_id]
        if service_info["running"]:
            webbrowser.open(service_info["url"])
        else:
            messagebox.showwarning("Service Not Running", 
                                 f"{service_info['name']} is not running. Please start it first.")
    
    def open_assistant(self):
        """Open Assistant application"""
        self.open_service("assistant")
    
    def open_voice_cloner(self):
        """Open Voice Cloning application"""
        self.open_service("voice_cloning")
    
    def open_dashboard(self):
        """Open Service Dashboard"""
        self.open_service("orchestrator")
    
    def open_monitor(self):
        """Open System Monitor"""
        try:
            subprocess.Popen(["taskmgr"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open System Monitor: {e}")
    
    def update_system_info(self):
        """Update system information display"""
        try:
            # Get system information
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get Python version
            python_version = sys.version.split()[0]
            
            # Get installation directory
            install_dir = os.path.dirname(__file__)
            
            info = f"""System Information:
CPU: {cpu_count} cores
Memory: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available
Disk: {disk.free / (1024**3):.1f} GB free of {disk.total / (1024**3):.1f} GB total

VoiceStudio Services:
- Assistant Service: Port 5080 (AI Assistant with Voice Cloning)
- Voice Cloning Service: Port 5081 (Advanced Voice Cloning Engine)
- Service Orchestrator: Port 5082 (Service Management Dashboard)

Installation Information:
Installation Directory: {install_dir}
Python Version: {python_version}
VoiceStudio Version: 1.0.0

Quick Start:
1. Click "Start All Services" to launch all VoiceStudio services
2. Use the "Open" buttons to access each service
3. Check the Service Dashboard for detailed monitoring
4. Use Voice Cloning Studio for advanced voice synthesis

Support:
For help and documentation, visit: https://voicestudio.ai
"""
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            
        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"Error loading system information: {e}")
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceStudioLauncher()
    app.run()
