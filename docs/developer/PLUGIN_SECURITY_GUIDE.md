# VoiceStudio Plugin Security Guide

Security best practices for plugin development and deployment.

## Overview

VoiceStudio plugins run with varying levels of trust and isolation. This guide covers security requirements, best practices, and common pitfalls to avoid.

## Security Model

### Trust Levels

| Level | Description | Isolation | Permissions |
|-------|-------------|-----------|-------------|
| **Trusted** | Built-in or verified publisher | In-process | Full access |
| **Standard** | Community plugins | Subprocess sandbox | Declared only |
| **Untrusted** | Unverified sources | Strict sandbox | Minimal |

### Permission System

Plugins must declare required permissions in their manifest:

```json
{
  "security": {
    "permissions": [
      "file_read",
      "file_write",
      "network_local",
      "network_internet",
      "subprocess",
      "gpu"
    ],
    "sandbox_mode": "subprocess"
  }
}
```

### Available Permissions

| Permission | Grants | Risk Level |
|------------|--------|------------|
| `file_read` | Read files in allowed directories | Low |
| `file_write` | Write files in allowed directories | Medium |
| `file_system` | Full file system access | High |
| `network_local` | Localhost network access | Low |
| `network_internet` | Internet access | High |
| `subprocess` | Spawn child processes | High |
| `gpu` | GPU/CUDA access | Medium |
| `clipboard` | Read/write clipboard | Medium |
| `notifications` | Show system notifications | Low |
| `microphone` | Access microphone | High |
| `camera` | Access camera | High |

## Security Requirements

### 1. Minimal Permissions

Request only the permissions your plugin actually needs.

```json
// ❌ BAD: Requesting everything
"permissions": ["file_system", "network_internet", "subprocess"]

// ✅ GOOD: Only what's needed
"permissions": ["file_read", "network_local"]
```

### 2. Input Validation

Always validate and sanitize user input.

```python
from voicestudio_sdk import Plugin
import re

class SecurePlugin(Plugin):
    MAX_TEXT_LENGTH = 10000
    ALLOWED_CHARS = re.compile(r'^[\w\s\.,!?\-\'\"]+$')
    
    async def process_text(self, text: str) -> str:
        # Length validation
        if not text:
            raise ValueError("Text cannot be empty")
        if len(text) > self.MAX_TEXT_LENGTH:
            raise ValueError(f"Text exceeds {self.MAX_TEXT_LENGTH} chars")
        
        # Character validation (if needed)
        if not self.ALLOWED_CHARS.match(text):
            raise ValueError("Text contains invalid characters")
        
        # Encoding safety
        text = text.encode('utf-8', errors='replace').decode('utf-8')
        
        return await self._process(text)
```

### 3. Path Validation

Never trust user-provided paths. Always validate and sanitize.

```python
from pathlib import Path

class SecurePlugin(Plugin):
    def validate_path(self, user_path: str, base_dir: Path) -> Path:
        """Safely resolve a user-provided path."""
        # Resolve to absolute path
        resolved = (base_dir / user_path).resolve()
        
        # Ensure path is within allowed directory (prevent path traversal)
        if not str(resolved).startswith(str(base_dir.resolve())):
            raise PermissionError("Path traversal detected")
        
        return resolved
    
    async def read_user_file(self, filename: str) -> bytes:
        allowed_dir = Path(self._config.get("data_dir", "./data"))
        safe_path = self.validate_path(filename, allowed_dir)
        
        return safe_path.read_bytes()
```

### 4. Secrets Management

Never expose or log secrets.

```python
# ❌ BAD: Logging secrets
self.host.log("debug", f"Using API key: {api_key}")

# ❌ BAD: Including secrets in errors
raise ValueError(f"Auth failed with key {api_key}")

# ✅ GOOD: Mask secrets in logs
self.host.log("debug", f"Using API key: {api_key[:4]}...{api_key[-4:]}")

# ✅ GOOD: Generic error messages
raise ValueError("Authentication failed - check API key")
```

Use PASSWORD config type for sensitive fields:

```python
config.add_field(ConfigField(
    name="api_key",
    field_type=ConfigType.PASSWORD,  # UI masks input
    label="API Key",
    required=True
))
```

### 5. Secure Network Access

When making network requests:

```python
import ssl
import aiohttp

class SecureNetworkPlugin(Plugin):
    async def fetch_data(self, url: str) -> bytes:
        # Validate URL scheme
        if not url.startswith(('https://', 'http://localhost')):
            raise ValueError("Only HTTPS or localhost allowed")
        
        # Use secure SSL context
        ssl_context = ssl.create_default_context()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                ssl=ssl_context,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                return await response.read()
```

### 6. Resource Cleanup

Always clean up resources, especially in error cases.

```python
class ResourceSafePlugin(Plugin):
    def __init__(self):
        self._temp_files: List[Path] = []
        self._connections: List[Connection] = []
    
    async def shutdown(self) -> None:
        """Clean up all resources."""
        # Clean temp files
        for temp_file in self._temp_files:
            try:
                temp_file.unlink(missing_ok=True)
            except Exception as e:
                self.host.log("warning", f"Cleanup failed: {e}")
        
        # Close connections
        for conn in self._connections:
            try:
                await conn.close()
            except Exception:
                pass
        
        self._temp_files.clear()
        self._connections.clear()
    
    async def process(self, audio: AudioBuffer) -> AudioBuffer:
        temp_path = None
        try:
            temp_path = self._create_temp_file(audio)
            self._temp_files.append(temp_path)
            result = await self._process_file(temp_path)
            return result
        finally:
            # Clean up even on error
            if temp_path and temp_path in self._temp_files:
                temp_path.unlink(missing_ok=True)
                self._temp_files.remove(temp_path)
```

## Common Vulnerabilities

### 1. Path Traversal

**Vulnerability**: Attacker accesses files outside allowed directories.

```python
# ❌ VULNERABLE
def read_file(self, filename: str) -> bytes:
    return open(f"./data/{filename}", "rb").read()

# Attack: filename = "../../../etc/passwd"
```

**Prevention**: Use path validation (see above).

### 2. Command Injection

**Vulnerability**: Attacker executes arbitrary commands.

```python
# ❌ VULNERABLE
import os
def convert_audio(self, input_file: str, output_format: str):
    os.system(f"ffmpeg -i {input_file} output.{output_format}")

# Attack: output_format = "wav; rm -rf /"
```

**Prevention**: Use subprocess with argument lists, validate input.

```python
# ✅ SAFE
import subprocess

ALLOWED_FORMATS = {"wav", "mp3", "flac", "ogg"}

def convert_audio(self, input_file: Path, output_format: str):
    if output_format not in ALLOWED_FORMATS:
        raise ValueError(f"Invalid format: {output_format}")
    
    # Validate input_file is within allowed directory
    input_file = self.validate_path(str(input_file))
    
    subprocess.run(
        ["ffmpeg", "-i", str(input_file), f"output.{output_format}"],
        check=True,
        capture_output=True
    )
```

### 3. Denial of Service

**Vulnerability**: Plugin consumes excessive resources.

```python
# ❌ VULNERABLE: No limits
async def process(self, text: str) -> str:
    return await self.model.generate(text)  # Could be 1GB of text
```

**Prevention**: Implement resource limits.

```python
# ✅ SAFE: Enforced limits
MAX_INPUT_LENGTH = 10000
MAX_OUTPUT_LENGTH = 50000
TIMEOUT_SECONDS = 60

async def process(self, text: str) -> str:
    if len(text) > MAX_INPUT_LENGTH:
        raise ValueError(f"Input exceeds {MAX_INPUT_LENGTH} chars")
    
    try:
        result = await asyncio.wait_for(
            self.model.generate(text),
            timeout=TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        raise RuntimeError("Processing timed out")
    
    if len(result) > MAX_OUTPUT_LENGTH:
        result = result[:MAX_OUTPUT_LENGTH]
        self.host.log("warning", "Output truncated")
    
    return result
```

### 4. Information Disclosure

**Vulnerability**: Plugin leaks sensitive information.

```python
# ❌ VULNERABLE: Exposes internal details
except Exception as e:
    raise RuntimeError(f"Error in {self._internal_path}: {e}")

# ✅ SAFE: Generic external message, detailed internal log
except Exception as e:
    self.host.log("error", f"Internal error: {e}")
    raise RuntimeError("Processing failed - see logs for details")
```

### 5. Insecure Deserialization

**Vulnerability**: Loading untrusted serialized data.

```python
# ❌ VULNERABLE: pickle can execute arbitrary code
import pickle
def load_model(self, path: str):
    return pickle.load(open(path, "rb"))
```

**Prevention**: Use safe formats or validate sources.

```python
# ✅ SAFE: Use safe formats
import json
import safetensors

def load_config(self, path: Path) -> dict:
    return json.loads(path.read_text())

def load_model(self, path: Path):
    # Use safetensors for ML models
    return safetensors.torch.load_file(path)
```

## Sandbox Modes

### Direct Mode (Trusted)

Plugin runs in the main process. Only for verified, trusted plugins.

```json
"security": {
    "sandbox_mode": "direct"
}
```

### Subprocess Mode (Standard)

Plugin runs in isolated subprocess with IPC communication.

```json
"security": {
    "sandbox_mode": "subprocess"
}
```

**Restrictions:**
- Cannot access parent process memory
- Limited to declared permissions
- Communication via structured IPC only
- Resource limits enforced

### Strict Mode (Untrusted)

Maximum isolation for untrusted plugins.

```json
"security": {
    "sandbox_mode": "strict"
}
```

**Additional restrictions:**
- No network access by default
- Read-only file system except temp directory
- CPU and memory limits
- Time limits on operations

## Security Checklist

Before publishing a plugin, verify:

### Permissions
- [ ] Only required permissions declared
- [ ] No unnecessary file system access
- [ ] No unnecessary network access
- [ ] Subprocess permission only if needed

### Input Handling
- [ ] All user input validated
- [ ] Path traversal prevented
- [ ] Injection attacks prevented
- [ ] Size limits enforced

### Secrets
- [ ] No hardcoded secrets
- [ ] Secrets use PASSWORD config type
- [ ] Secrets not logged or exposed in errors
- [ ] API keys retrieved from config only

### Error Handling
- [ ] No internal details in user-facing errors
- [ ] Resources cleaned up on errors
- [ ] Graceful handling of unexpected input

### Dependencies
- [ ] Dependencies from trusted sources
- [ ] No known vulnerable versions
- [ ] Minimal dependency footprint

### Testing
- [ ] Security test cases included
- [ ] Boundary conditions tested
- [ ] Malicious input tested

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** disclose publicly
2. Email security@voicestudio.app with details
3. Include reproduction steps
4. Allow 90 days for fix before disclosure

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)
- [VoiceStudio Security Policy](../../SECURITY.md)
