#!/usr/bin/env python3
"""
VoiceStudio Production Deployment Scripts
Handles Docker containerization, service orchestration, and production deployment.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
import yaml

class DockerManager:
    """Manages Docker containerization"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services = {
            "assistant": {"port": 5080, "file": "services/assistant/enhanced_service.py"},
            "orchestrator": {"port": 5090, "file": "services/orchestrator/service.py"},
            "autofix": {"port": 5081, "file": "services/autofix/service.py"}
        }
    
    def create_dockerfile(self, service_name: str) -> str:
        """Create Dockerfile for a service"""
        dockerfile_content = f"""FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service files
COPY services/ ./services/
COPY config/ ./config/

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE {self.services[service_name]['port']}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:{self.services[service_name]['port']}/health')"

# Run the service
CMD ["python", "{self.services[service_name]['file']}"]
"""
        return dockerfile_content
    
    def create_requirements_txt(self) -> str:
        """Create requirements.txt for all services"""
        requirements = """requests>=2.31.0
PyJWT>=2.8.0
cryptography>=41.0.0
psycopg2-binary>=2.9.0
sqlite3
pyyaml>=6.0
"""
        return requirements
    
    def create_docker_compose(self) -> str:
        """Create docker-compose.yml for all services"""
        compose_content = """version: '3.8'

services:
  assistant:
    build:
      context: .
      dockerfile: Dockerfile.assistant
    ports:
      - "5080:5080"
    environment:
      - SERVICE_NAME=assistant
      - SERVICE_PORT=5080
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
    networks:
      - voicestudio-network

  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile.orchestrator
    ports:
      - "5090:5090"
    environment:
      - SERVICE_NAME=orchestrator
      - SERVICE_PORT=5090
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
    networks:
      - voicestudio-network

  autofix:
    build:
      context: .
      dockerfile: Dockerfile.autofix
    ports:
      - "5081:5081"
    environment:
      - SERVICE_NAME=autofix
      - SERVICE_PORT=5081
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
    networks:
      - voicestudio-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=voicestudio
      - POSTGRES_USER=voicestudio
      - POSTGRES_PASSWORD=voicestudio_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    networks:
      - voicestudio-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - assistant
      - orchestrator
      - autofix
    networks:
      - voicestudio-network

volumes:
  postgres_data:

networks:
  voicestudio-network:
    driver: bridge
"""
        return compose_content
    
    def create_nginx_config(self) -> str:
        """Create nginx configuration"""
        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream assistant {
        server assistant:5080;
    }
    
    upstream orchestrator {
        server orchestrator:5090;
    }
    
    upstream autofix {
        server autofix:5081;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Assistant service
        location /assistant/ {
            proxy_pass http://assistant/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Orchestrator service
        location /orchestrator/ {
            proxy_pass http://orchestrator/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Autofix service
        location /autofix/ {
            proxy_pass http://autofix/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
"""
        return nginx_config
    
    def create_init_db_sql(self) -> str:
        """Create database initialization SQL"""
        init_sql = """-- VoiceStudio Database Initialization

CREATE DATABASE voicestudio;
\\c voicestudio;

-- Service logs table
CREATE TABLE IF NOT EXISTS service_logs (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    level VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    metadata JSONB
);

-- Service metrics table
CREATE TABLE IF NOT EXISTS service_metrics (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    tags JSONB
);

-- Configuration table
CREATE TABLE IF NOT EXISTS configurations (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Service registry table
CREATE TABLE IF NOT EXISTS service_registry (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(255) UNIQUE NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    health_endpoint VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    last_heartbeat TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_service_logs_service_id ON service_logs(service_id);
CREATE INDEX IF NOT EXISTS idx_service_logs_timestamp ON service_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_service_metrics_service_id ON service_metrics(service_id);
CREATE INDEX IF NOT EXISTS idx_service_metrics_timestamp ON service_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_service_metrics_name ON service_metrics(metric_name);

-- Insert default configuration
INSERT INTO configurations (key, value, service_name, created_at, updated_at) VALUES
('app_version', '1.0.0', 'system', NOW(), NOW()),
('environment', 'production', 'system', NOW(), NOW()),
('log_level', 'INFO', 'system', NOW(), NOW())
ON CONFLICT (key) DO NOTHING;
"""
        return init_sql
    
    def generate_deployment_files(self):
        """Generate all deployment files"""
        print("Generating deployment files...")
        
        # Create requirements.txt
        requirements_path = self.project_root / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(self.create_requirements_txt())
        print(f"Created {requirements_path}")
        
        # Create Dockerfiles for each service
        for service_name in self.services:
            dockerfile_path = self.project_root / f"Dockerfile.{service_name}"
            with open(dockerfile_path, 'w') as f:
                f.write(self.create_dockerfile(service_name))
            print(f"Created {dockerfile_path}")
        
        # Create docker-compose.yml
        compose_path = self.project_root / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write(self.create_docker_compose())
        print(f"Created {compose_path}")
        
        # Create nginx directory and config
        nginx_dir = self.project_root / "nginx"
        nginx_dir.mkdir(exist_ok=True)
        
        nginx_config_path = nginx_dir / "nginx.conf"
        with open(nginx_config_path, 'w') as f:
            f.write(self.create_nginx_config())
        print(f"Created {nginx_config_path}")
        
        # Create scripts directory and init SQL
        scripts_dir = self.project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        init_sql_path = scripts_dir / "init-db.sql"
        with open(init_sql_path, 'w') as f:
            f.write(self.create_init_db_sql())
        print(f"Created {init_sql_path}")
        
        print("Deployment files generated successfully!")

class DeploymentManager:
    """Manages deployment operations"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docker_manager = DockerManager(project_root)
    
    def build_images(self):
        """Build Docker images for all services"""
        print("Building Docker images...")
        
        for service_name in self.docker_manager.services:
            print(f"Building {service_name} image...")
            result = subprocess.run([
                "docker", "build", 
                "-f", f"Dockerfile.{service_name}",
                "-t", f"voicestudio-{service_name}:latest",
                "."
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ {service_name} image built successfully")
            else:
                print(f"✗ Failed to build {service_name} image: {result.stderr}")
                return False
        
        return True
    
    def start_services(self):
        """Start all services using docker-compose"""
        print("Starting services with docker-compose...")
        
        result = subprocess.run([
            "docker-compose", "up", "-d"
        ], cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All services started successfully")
            return True
        else:
            print(f"✗ Failed to start services: {result.stderr}")
            return False
    
    def stop_services(self):
        """Stop all services"""
        print("Stopping services...")
        
        result = subprocess.run([
            "docker-compose", "down"
        ], cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All services stopped")
            return True
        else:
            print(f"✗ Failed to stop services: {result.stderr}")
            return False
    
    def check_services(self):
        """Check service health"""
        print("Checking service health...")
        
        services = [
            ("Assistant", "http://localhost:5080/health"),
            ("Orchestrator", "http://localhost:5090/health"),
            ("Autofix", "http://localhost:5081/health")
        ]
        
        import requests
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✓ {name} service is healthy")
                else:
                    print(f"✗ {name} service returned status {response.status_code}")
            except Exception as e:
                print(f"✗ {name} service is not responding: {e}")
    
    def deploy(self):
        """Full deployment process"""
        print("Starting VoiceStudio deployment...")
        
        # Generate deployment files
        self.docker_manager.generate_deployment_files()
        
        # Build images
        if not self.build_images():
            print("Deployment failed at image building stage")
            return False
        
        # Start services
        if not self.start_services():
            print("Deployment failed at service startup stage")
            return False
        
        # Wait for services to start
        print("Waiting for services to start...")
        import time
        time.sleep(10)
        
        # Check service health
        self.check_services()
        
        print("Deployment completed successfully!")
        print("\nService URLs:")
        print("- Assistant: http://localhost:5080")
        print("- Orchestrator: http://localhost:5090")
        print("- Autofix: http://localhost:5081")
        print("- Nginx Proxy: http://localhost:80")
        
        return True

def main():
    """Main deployment script"""
    if len(sys.argv) < 2:
        print("Usage: python deploy.py <command>")
        print("Commands: generate, build, start, stop, check, deploy")
        return
    
    command = sys.argv[1]
    project_root = os.getcwd()
    deployment_manager = DeploymentManager(project_root)
    
    if command == "generate":
        deployment_manager.docker_manager.generate_deployment_files()
    elif command == "build":
        deployment_manager.build_images()
    elif command == "start":
        deployment_manager.start_services()
    elif command == "stop":
        deployment_manager.stop_services()
    elif command == "check":
        deployment_manager.check_services()
    elif command == "deploy":
        deployment_manager.deploy()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
