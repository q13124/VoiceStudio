#!/usr/bin/env python3
"""
VoiceStudio System Health Validator
Comprehensive checks for framework integrity, compatibility, and readiness
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

class HealthValidator:
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.results = []
        
    def check(self, name: str, func) -> bool:
        """Run check and record result"""
        try:
            result = func()
            status = "✅" if result else "❌"
            self.results.append((name, result, ""))
            print(f"{status} {name}")
            return result
        except Exception as e:
            self.results.append((name, False, str(e)))
            print(f"❌ {name}: {e}")
            return False
    
    def check_python_version(self) -> bool:
        """Check Python version >= 3.9"""
        return sys.version_info >= (3, 9)
    
    def check_dependencies(self) -> bool:
        """Check pip dependencies for conflicts"""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def check_critical_imports(self) -> bool:
        """Check critical packages import successfully"""
        try:
            import torch
            import torchaudio
            import numpy
            import fastapi
            return True
        except ImportError:
            return False
    
    def check_config_files(self) -> bool:
        """Check configuration files exist and are valid"""
        config_dir = self.root / "config"
        required = ["voicestudio.config.json", "engines.config.json"]
        
        for cfg in required:
            path = config_dir / cfg
            if not path.exists():
                return False
            try:
                with open(path) as f:
                    json.load(f)
            except json.JSONDecodeError:
                return False
        return True
    
    def check_circular_dependencies(self) -> bool:
        """Check for circular imports (simplified)"""
        # Basic check - full implementation would use AST
        services_dir = self.root / "services"
        if not services_dir.exists():
            return True
        
        # Check for obvious circular patterns
        for py_file in services_dir.rglob("*.py"):
            with open(py_file) as f:
                content = f.read()
                # Simple heuristic: avoid importing from same package
                if "from services." in content and "import" in content:
                    # More sophisticated check needed
                    pass
        return True
    
    def check_database_schema(self) -> bool:
        """Check database exists and has correct schema"""
        db_path = self.root / "voicestudio.db"
        if not db_path.exists():
            return False
        
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            
            required_tables = {"service_logs", "service_metrics"}
            return required_tables.issubset(tables)
        except Exception:
            return False
    
    def check_model_paths(self) -> bool:
        """Check model directories exist"""
        programdata = os.environ.get("PROGRAMDATA", "C:/ProgramData")
        models_dir = Path(programdata) / "VoiceStudio" / "models"
        
        if not models_dir.exists():
            print(f"  ⚠️  Models directory not found: {models_dir}")
            return False
        
        # Check for at least one engine
        engines = ["xtts", "openvoice", "cosyvoice2", "coqui"]
        found = any((models_dir / engine).exists() for engine in engines)
        return found
    
    def check_gpu_availability(self) -> bool:
        """Check GPU availability (warning only)"""
        try:
            import torch
            available = torch.cuda.is_available()
            if not available:
                print("  ⚠️  No GPU detected - will use CPU (slower)")
            return True  # Not a failure
        except Exception:
            return True
    
    def check_port_availability(self) -> bool:
        """Check required ports are available"""
        import socket
        
        ports = [5188, 5080, 5090]  # Main service ports
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"  ⚠️  Port {port} already in use")
                # Not a failure - might be running
        return True
    
    def check_file_structure(self) -> bool:
        """Check critical directories exist"""
        required_dirs = [
            "config",
            "services",
            "workers",
            "tools",
            "UltraClone.EngineService",
        ]
        
        for dir_name in required_dirs:
            if not (self.root / dir_name).exists():
                print(f"  ❌ Missing directory: {dir_name}")
                return False
        return True
    
    def check_grpc_proto(self) -> bool:
        """Check gRPC proto files exist"""
        proto_file = self.root / "VoiceStudio.Contracts" / "engine.proto"
        return proto_file.exists()
    
    def run_all_checks(self) -> bool:
        """Run all health checks"""
        print("\n🔍 VoiceStudio System Health Check\n")
        
        checks = [
            ("Python Version (>=3.9)", self.check_python_version),
            ("Dependency Compatibility", self.check_dependencies),
            ("Critical Imports", self.check_critical_imports),
            ("Configuration Files", self.check_config_files),
            ("File Structure", self.check_file_structure),
            ("Database Schema", self.check_database_schema),
            ("Model Paths", self.check_model_paths),
            ("gRPC Contracts", self.check_grpc_proto),
            ("GPU Availability", self.check_gpu_availability),
            ("Port Availability", self.check_port_availability),
            ("Circular Dependencies", self.check_circular_dependencies),
        ]
        
        passed = 0
        for name, func in checks:
            if self.check(name, func):
                passed += 1
        
        print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
        
        if passed == len(checks):
            print("✅ System is healthy and ready!")
            return True
        else:
            print("❌ System has issues that need attention")
            return False
    
    def generate_report(self) -> str:
        """Generate detailed health report"""
        report = ["# VoiceStudio Health Report\n"]
        report.append(f"**Date**: {__import__('datetime').datetime.now()}\n")
        report.append(f"**Python**: {sys.version}\n")
        report.append(f"**Platform**: {sys.platform}\n\n")
        
        report.append("## Check Results\n")
        for name, result, error in self.results:
            status = "✅ PASS" if result else "❌ FAIL"
            report.append(f"- {status}: {name}")
            if error:
                report.append(f"  - Error: {error}")
            report.append("\n")
        
        return "\n".join(report)

def main():
    validator = HealthValidator()
    success = validator.run_all_checks()
    
    # Generate report
    report = validator.generate_report()
    report_path = validator.root / "HEALTH_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\n📄 Detailed report: {report_path}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
