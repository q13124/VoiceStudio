#!/usr/bin/env python3
"""
VoiceStudio Configuration Optimizer
Automatically optimizes configuration settings for better performance.
"""

import json
import os
import logging
from typing import Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigurationOptimizer:
    """Optimizes VoiceStudio configuration for better performance"""
    
    def __init__(self):
        self.config_path = Path("config/appsettings.json")
        self.backup_path = Path("config/appsettings.json.backup")
    
    def backup_config(self):
        """Create backup of current configuration"""
        if self.config_path.exists():
            import shutil
            shutil.copy2(self.config_path, self.backup_path)
            logger.info(f"Configuration backed up to {self.backup_path}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load current configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save optimized configuration"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Optimized configuration saved to {self.config_path}")
    
    def optimize_config(self) -> Dict[str, Any]:
        """Generate optimized configuration"""
        current_config = self.load_config()
        
        # Optimized configuration with performance improvements
        optimized_config = {
            "Services": {
                "Assistant": {
                    "Port": 5080,
                    "HealthEndpoint": "/health",
                    "AutofixEndpoint": "/autofix/status",
                    "MaxWorkers": 10,
                    "ConnectionPoolSize": 20,
                    "RequestTimeout": 30,
                    "EnableCaching": True,
                    "CacheTTL": 300
                },
                "Orchestrator": {
                    "Port": 5090,
                    "HealthEndpoint": "/health",
                    "SettingsEndpoint": "/settings",
                    "WeightsEndpoint": "/weights",
                    "MaxWorkers": 8,
                    "ConnectionPoolSize": 15,
                    "RequestTimeout": 30,
                    "EnableCaching": True,
                    "CacheTTL": 300
                },
                "Autofix": {
                    "Port": 5081,
                    "HealthEndpoint": "/health",
                    "StatusEndpoint": "/status",
                    "AnalyzeEndpoint": "/analyze",
                    "MaxWorkers": 6,
                    "ConnectionPoolSize": 10,
                    "RequestTimeout": 30,
                    "EnableCaching": True,
                    "CacheTTL": 300
                }
            },
            "Database": {
                "Type": "sqlite",
                "Path": "voicestudio.db",
                "PoolSize": 10,
                "ConnectionTimeout": 30,
                "EnableWAL": True,
                "Synchronous": "NORMAL",
                "CacheSize": 10000,
                "TempStore": "MEMORY",
                "EnableIndexes": True,
                "CleanupInterval": 86400,  # 24 hours
                "RetentionDays": 30
            },
            "ServiceDiscovery": {
                "HeartbeatInterval": 30,
                "HealthCheckTimeout": 5,
                "MaxWorkers": 10,
                "SessionPoolSize": 20,
                "EnableCaching": True,
                "CacheTTL": 10,
                "ParallelHealthChecks": True
            },
            "Security": {
                "JWTExpirationHours": 24,
                "APIKeyLength": 32,
                "EnableTokenBlacklisting": True,
                "MaxLoginAttempts": 5,
                "LockoutDuration": 300
            },
            "AudioProcessing": {
                "MaxWorkers": 4,
                "EnableParallelProcessing": True,
                "EnableCaching": True,
                "CacheTTL": 300,
                "MaxFileSize": 100 * 1024 * 1024,  # 100MB
                "SupportedFormats": ["wav", "mp3", "m4a", "flac"]
            },
            "Performance": {
                "EnableMetrics": True,
                "MetricsInterval": 60,
                "EnableProfiling": False,
                "LogLevel": "INFO",
                "MaxLogSize": 10 * 1024 * 1024,  # 10MB
                "LogRetentionDays": 7
            },
            "Caching": {
                "EnableRedis": False,
                "RedisHost": "localhost",
                "RedisPort": 6379,
                "RedisDB": 0,
                "EnableInMemoryCache": True,
                "MaxCacheSize": 1000,
                "DefaultTTL": 300
            },
            "Monitoring": {
                "EnableHealthChecks": True,
                "HealthCheckInterval": 30,
                "EnableMetrics": True,
                "MetricsEndpoint": "/metrics",
                "EnablePrometheus": False,
                "PrometheusPort": 9090
            }
        }
        
        # Merge with existing config, preserving user settings
        merged_config = self._merge_configs(current_config, optimized_config)
        return merged_config
    
    def _merge_configs(self, current: Dict[str, Any], optimized: Dict[str, Any]) -> Dict[str, Any]:
        """Merge current config with optimized config, preserving user settings"""
        merged = optimized.copy()
        
        # Recursively merge configurations
        for key, value in current.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_configs(value, merged[key])
                else:
                    # Preserve user's custom values
                    merged[key] = value
            else:
                # Add user's custom keys
                merged[key] = value
        
        return merged
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration for correctness"""
        try:
            # Check required services
            required_services = ["Assistant", "Orchestrator", "Autofix"]
            services = config.get("Services", {})
            
            for service in required_services:
                if service not in services:
                    logger.error(f"Missing required service: {service}")
                    return False
                
                service_config = services[service]
                if "Port" not in service_config:
                    logger.error(f"Missing port for service: {service}")
                    return False
            
            # Check port conflicts
            ports = []
            for service_name, service_config in services.items():
                port = service_config.get("Port")
                if port in ports:
                    logger.error(f"Port conflict: {port} used by multiple services")
                    return False
                ports.append(port)
            
            # Check database configuration
            db_config = config.get("Database", {})
            if db_config.get("PoolSize", 0) <= 0:
                logger.warning("Database pool size should be greater than 0")
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def generate_performance_tips(self) -> list:
        """Generate performance optimization tips"""
        tips = [
            {
                "category": "Database",
                "tip": "Use connection pooling to reduce connection overhead",
                "impact": "High"
            },
            {
                "category": "Database",
                "tip": "Enable WAL mode for better concurrency",
                "impact": "High"
            },
            {
                "category": "Database",
                "tip": "Add indexes on frequently queried columns",
                "impact": "High"
            },
            {
                "category": "Service Discovery",
                "tip": "Use parallel health checks to reduce monitoring overhead",
                "impact": "Medium"
            },
            {
                "category": "Service Discovery",
                "tip": "Implement HTTP session pooling for better performance",
                "impact": "Medium"
            },
            {
                "category": "Audio Processing",
                "tip": "Process multiple audio files in parallel",
                "impact": "High"
            },
            {
                "category": "Audio Processing",
                "tip": "Cache file metadata to avoid repeated file system calls",
                "impact": "Medium"
            },
            {
                "category": "Caching",
                "tip": "Enable in-memory caching for frequently accessed data",
                "impact": "High"
            },
            {
                "category": "Caching",
                "tip": "Use Redis for distributed caching in multi-instance deployments",
                "impact": "Medium"
            },
            {
                "category": "Monitoring",
                "tip": "Enable metrics collection for performance monitoring",
                "impact": "Low"
            }
        ]
        return tips

def main():
    """Main function for configuration optimization"""
    optimizer = ConfigurationOptimizer()
    
    try:
        # Backup current configuration
        optimizer.backup_config()
        
        # Generate optimized configuration
        logger.info("Generating optimized configuration...")
        optimized_config = optimizer.optimize_config()
        
        # Validate configuration
        if optimizer.validate_config(optimized_config):
            # Save optimized configuration
            optimizer.save_config(optimized_config)
            logger.info("Configuration optimization completed successfully!")
            
            # Display performance tips
            tips = optimizer.generate_performance_tips()
            print("\n=== Performance Optimization Tips ===")
            for tip in tips:
                print(f"\n{tip['category']}: {tip['tip']}")
                print(f"Impact: {tip['impact']}")
        else:
            logger.error("Configuration optimization failed validation")
            
    except Exception as e:
        logger.error(f"Configuration optimization failed: {e}")

if __name__ == "__main__":
    main()
