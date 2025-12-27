# Technical Strategy: Legacy Engine Isolation Architecture
**Project:** VoiceStudio  
**Author:** Senior Systems Architect  
**Date:** 2025-01-28  
**Context:** Integration of Tortoise TTS (Legacy Stack) into VoiceStudio (Modern Stack)

---

## 1. Executive Summary
The requirement to run conflicting dependency stacks (PyTorch 2.0 vs Modern) within a single seamless Windows desktop application necessitates a **Polyglot Subprocess Architecture**. 

We will reject Docker-based solutions due to high user friction (requirement for virtualization support/WSL2). We will reject "patching" legacy engines as it incurs high technical debt.

**Recommended Solution:** The **"Managed Venv Sidecar" Pattern**.  
The main application acts as an orchestrator, creating and managing a hidden, dedicated Python virtual environment for the legacy engine. Communication is handled via **ZeroMQ (ZMQ)** for low-latency IPC (Inter-Process Communication).

---

## 2. Architecture Overview

### The "Hub and Spoke" Model
* **The Hub (Main Process):** Handles UI, audio playback, user inputs, and high-level logic.
* **The Spoke (Worker Process):** A headless Python script running inside a dedicated virtual environment.

| Feature | Main App (Hub) | Legacy Engine (Spoke) |
| :--- | :--- | :--- |
| **Runtime** | Python 3.11 (System/Installer) | Python 3.10 (Managed Venv) |
| **Dependencies** | Modern Torch, PyQt/Tkinter, SQL | Old Torch, Tortoise, SciPy |
| **Role** | Orchestrator & UI | Compute Node |
| **Communication** | ZMQ Request (Client) | ZMQ Reply (Server) |

---

## 3. Implementation Details

### A. The Hidden Environment Strategy
To ensure the "seamless" UX requested, the user must never manually type `pip install`.

**Workflow:**
1.  **Detection:** Main App launches and checks for `./engines/tortoise_env`.
2.  **Creation:** If missing, Main App runs `python -m venv ./engines/tortoise_env`.
3.  **Provisioning:** Main App calls the *venv's pip* to install requirements:
    ```bash
    ./engines/tortoise_env/Scripts/pip install -r tortoise_requirements.txt
    ```
4.  **Feedback:** The UI displays a "Configuring AI Models..." spinner during this one-time setup.

### B. IPC Protocol (ZeroMQ)
We choose **ZeroMQ (ZMQ)** over standard HTTP (FastAPI/Flask) or raw pipes.
* **Why ZMQ?** It is brokerless, supports "Request-Reply" natively, and is faster than HTTP overhead.
* **Data Transport:** 
    * **Control:** JSON payloads for configuration (text, voice, emotion).
    * **Audio:** For short clips, Base64 encoded strings within JSON. For long generation, the worker writes to a temporary directory and returns the **filepath**.

### C. GPU VRAM Management
This is the critical failure point for local AI apps.
* **Protocol:** Implement a "Baton Pass" system.
* The Main App must unload its own heavy models (move to CPU or delete) *before* sending the `start` command to the worker.
* The Worker initializes lazily. It does not load weights until the first `infer` request is received.

---

## 4. Code Implementation Blueprints

### Component 1: The Orchestrator (Main App)
*Runs in the Modern Environment.*

```python
import subprocess
import zmq
import json
import os
import sys

class TortoiseClient:
    def __init__(self, venv_path, worker_script_path):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        # Dynamic port selection recommended for production
        self.port = 5555 
        
        # Path handling for Windows
        self.python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        self.worker_script = worker_script_path
        self.process = None

    def start_service(self):
        """Spawns the legacy environment in the background"""
        cmd = [self.python_exe, self.worker_script, "--port", str(self.port)]
        
        # Windows: Prevent cmd window popping up
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        print(f"Starting Worker: {' '.join(cmd)}")
        self.process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Connect to the socket (Worker binds, we connect)
        self.socket.connect(f"tcp://localhost:{self.port}")

    def generate(self, text, voice="angie"):
        """Blocking call to generate audio"""
        payload = {
            "command": "generate",
            "text": text,
            "voice": voice
        }
        
        try:
            # 1. Send Request
            self.socket.send_json(payload)
            
            # 2. Wait for Reply (Consider using a Poller for timeout handling)
            response = self.socket.recv_json()
            
            if response['status'] == 'error':
                raise Exception(f"Worker Error: {response['message']}")
                
            return response['file_path']
            
        except zmq.ZMQError as e:
            print(f"Communication error: {e}")
            return None

    def shutdown(self):
        """Graceful cleanup"""
        if self.process:
            self.process.terminate()
            self.process.wait()
```

### Component 2: The Worker (Legacy App)
*Runs in the Legacy Environment. Cannot import modern libraries.*

```python
import sys
import zmq
import json
import argparse
import traceback
# import torch (imported lazily inside handler to speed up startup)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, default="5555")
    args = parser.parse_args()

    context = zmq.Context()
    socket = context.socket(zmq.REP) # Reply socket
    socket.bind(f"tcp://*:{args.port}")

    print(f"Worker running on port {args.port}")

    # Lazy loading global for the model
    tts_engine = None 

    while True:
        # 1. Wait for request
        message = socket.recv_json()
        command = message.get('command')
        
        response = {"status": "ok"}
        
        try:
            if command == "generate":
                # Lazy Load Logic
                if tts_engine is None:
                    print("Loading Tortoise...")
                    # from tortoise.api import TextToSpeech
                    # tts_engine = TextToSpeech()
                    pass # Mocking load

                text = message['text']
                # Run inference...
                # Save to temp file...
                output_path = f"temp_output_{hash(text)}.wav"
                
                response["file_path"] = output_path
                
            elif command == "ping":
                response["message"] = "pong"

        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
            response["traceback"] = traceback.format_exc()

        # 2. Send reply
        socket.send_json(response)

if __name__ == "__main__":
    main()
```

## 5. Risk Assessment & Mitigations

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| Zombie Processes | High | Main App must implement atexit handlers to kill() worker subprocesses if the main app crashes. |
| Port Conflicts | Medium | Use socket.bind(0) in the worker to grab a random free port, print it to stdout, and have Main App read stdout to discover the port. |
| Dependency Installation | High | Ship a requirements.txt specifically for Tortoise. Use pip install --no-index --find-links=./wheels if offline installation is required. |
| Model Download | Medium | Tortoise auto-downloads models to ~/.cache. Pre-bundle these models in your installer to avoid runtime download errors. |

## 6. Comparison to Research Alternatives

**Ref: Research Questions 1 & 2**

- **Subprocess Isolation (Selected):** Best performance, invisible to user.
- **Docker:** Too much overhead (File I/O slowness on Windows) and requires Admin privileges/BIOS virtualization.
- **HTTP Wrappers:** Adds HTTP parsing overhead. ZMQ is closer to "metal" for Python-to-Python comms.

## 7. Next Steps

1. **Prototype:** Create the DependencyManager class to automate the creation of the legacy venv.
2. **Benchmark:** Measure the time it takes to "Cold Start" the worker (process spawn + import torch).
3. **Integration:** Implement the Unload/Load VRAM logic in the main application.

