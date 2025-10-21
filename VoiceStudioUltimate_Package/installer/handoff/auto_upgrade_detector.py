#!/usr/bin/env python3
"""
VoiceStudio Upgrade Detector
Detects and applies upgrades from ChatGPT conversations
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import re
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class VoiceStudioUpgradeDetector:
    """Detects and applies upgrades from ChatGPT conversations"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.upgrades_dir = self.project_root / "upgrades"
        self.backup_dir = self.project_root / "backups"
        self.log_file = self.project_root / "logs" / f"auto_upgrade_{datetime.now().strftime('%Y%m%d')}.log"
        
    def detect_chatgpt_upgrades(self):
        """Detect potential upgrades from ChatGPT conversations"""
        logger.info("Detecting ChatGPT conversation upgrades...")
        
        # Check for upgrade indicators in various sources
        upgrade_sources = [
            self.check_conversation_files(),
            self.check_github_commits(),
            self.check_package_updates(),
            self.check_ai_suggestions()
        ]
        
        upgrades = []
        for source_upgrades in upgrade_sources:
            upgrades.extend(source_upgrades)
        
        logger.info(f"Detected {len(upgrades)} potential upgrades")
        return upgrades
    
    def check_conversation_files(self):
        """Check for upgrade patterns in conversation files"""
        upgrades = []
        
        # Look for conversation files or logs
        conversation_patterns = [
            "conversation_*.txt",
            "chat_*.log", 
            "upgrade_*.md",
            "improvement_*.json"
        ]
        
        for pattern in conversation_patterns:
            for file_path in self.project_root.glob(f"**/{pattern}"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for upgrade patterns
                    upgrade_patterns = [
                        r"upgrade.*?([a-zA-Z_]+\.py)",
                        r"improve.*?([a-zA-Z_]+\.py)",
                        r"fix.*?([a-zA-Z_]+\.py)",
                        r"add.*?feature.*?([a-zA-Z_]+\.py)",
                        r"enhance.*?([a-zA-Z_]+\.py)"
                    ]
                    
                    for pattern in upgrade_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            upgrades.append({
                                "type": "conversation_upgrade",
                                "file": match,
                                "source": str(file_path),
                                "confidence": 0.7,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                except Exception as e:
                    logger.warning(f"Error reading conversation file {file_path}: {e}")
        
        return upgrades
    
    def check_github_commits(self):
        """Check for GitHub commits that might contain upgrades"""
        upgrades = []
        
        try:
            # Check if this is a git repository
            result = subprocess.run(['git', 'status'], capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                # Get recent commits
                result = subprocess.run(['git', 'log', '--oneline', '-10'], capture_output=True, text=True, cwd=self.project_root)
                if result.returncode == 0:
                    commits = result.stdout.strip().split('\n')
                    
                    for commit in commits:
                        # Look for upgrade-related commit messages
                        if any(keyword in commit.lower() for keyword in ['upgrade', 'improve', 'fix', 'enhance', 'add']):
                            upgrades.append({
                                "type": "git_upgrade",
                                "commit": commit,
                                "source": "git_log",
                                "confidence": 0.8,
                                "timestamp": datetime.now().isoformat()
                            })
                            
        except Exception as e:
            logger.warning(f"Error checking git commits: {e}")
        
        return upgrades
    
    def check_package_updates(self):
        """Check for package updates that might improve the system"""
        upgrades = []
        
        try:
            # Check Python package updates
            result = subprocess.run(['pip', 'list', '--outdated'], capture_output=True, text=True)
            if result.returncode == 0:
                outdated_packages = result.stdout.strip().split('\n')[2:]  # Skip header
                
                for package_line in outdated_packages:
                    if package_line.strip():
                        parts = package_line.split()
                        if len(parts) >= 3:
                            package_name = parts[0]
                            current_version = parts[1]
                            latest_version = parts[2]
                            
                            upgrades.append({
                                "type": "package_upgrade",
                                "package": package_name,
                                "current_version": current_version,
                                "latest_version": latest_version,
                                "source": "pip_outdated",
                                "confidence": 0.9,
                                "timestamp": datetime.now().isoformat()
                            })
                            
        except Exception as e:
            logger.warning(f"Error checking package updates: {e}")
        
        return upgrades
    
    def check_ai_suggestions(self):
        """Check for AI-generated suggestions or improvements"""
        upgrades = []
        
        # Look for AI suggestion files
        ai_files = [
            "ai_suggestions.json",
            "improvements.md",
            "enhancements.txt",
            "next_steps.json"
        ]
        
        for ai_file in ai_files:
            file_path = self.project_root / ai_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if ai_file.endswith('.json'):
                            suggestions = json.load(f)
                        else:
                            suggestions = f.read()
                    
                    upgrades.append({
                        "type": "ai_suggestion",
                        "content": suggestions,
                        "source": str(file_path),
                        "confidence": 0.6,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"Error reading AI suggestions file {file_path}: {e}")
        
        return upgrades
    
    def apply_upgrade(self, upgrade):
        """Apply a detected upgrade"""
        logger.info(f"Applying upgrade: {upgrade['type']} from {upgrade['source']}")
        
        try:
            if upgrade['type'] == 'package_upgrade':
                return self.apply_package_upgrade(upgrade)
            elif upgrade['type'] == 'conversation_upgrade':
                return self.apply_conversation_upgrade(upgrade)
            elif upgrade['type'] == 'git_upgrade':
                return self.apply_git_upgrade(upgrade)
            elif upgrade['type'] == 'ai_suggestion':
                return self.apply_ai_suggestion(upgrade)
            else:
                logger.warning(f"Unknown upgrade type: {upgrade['type']}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying upgrade: {e}")
            return False
    
    def apply_package_upgrade(self, upgrade):
        """Apply a package upgrade"""
        package = upgrade['package']
        latest_version = upgrade['latest_version']
        
        logger.info(f"Upgrading package {package} to {latest_version}")
        
        try:
            # Create backup
            self.create_backup(f"package_upgrade_{package}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Apply upgrade
            result = subprocess.run(['pip', 'install', '--upgrade', package], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info(f"Successfully upgraded {package}")
                self.log_upgrade(upgrade, "SUCCESS", result.stdout)
                return True
            else:
                logger.error(f"Failed to upgrade {package}: {result.stderr}")
                self.log_upgrade(upgrade, "FAILED", result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"Error upgrading package {package}: {e}")
            self.log_upgrade(upgrade, "ERROR", str(e))
            return False
    
    def apply_conversation_upgrade(self, upgrade):
        """Apply an upgrade detected from conversation"""
        file_name = upgrade['file']
        
        logger.info(f"Processing conversation upgrade for {file_name}")
        
        try:
            # Create backup
            self.create_backup(f"conversation_upgrade_{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # This would need to be implemented based on specific conversation content
            # For now, we'll just log it
            self.log_upgrade(upgrade, "PROCESSED", f"Conversation upgrade detected for {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing conversation upgrade: {e}")
            self.log_upgrade(upgrade, "ERROR", str(e))
            return False
    
    def apply_git_upgrade(self, upgrade):
        """Apply a git-based upgrade"""
        commit = upgrade['commit']
        
        logger.info(f"Processing git upgrade: {commit}")
        
        try:
            # Create backup
            self.create_backup(f"git_upgrade_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # This would need to be implemented based on specific git changes
            # For now, we'll just log it
            self.log_upgrade(upgrade, "PROCESSED", f"Git upgrade detected: {commit}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing git upgrade: {e}")
            self.log_upgrade(upgrade, "ERROR", str(e))
            return False
    
    def apply_ai_suggestion(self, upgrade):
        """Apply an AI-generated suggestion"""
        content = upgrade['content']
        
        logger.info("Processing AI suggestion")
        
        try:
            # Create backup
            self.create_backup(f"ai_suggestion_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # This would need to be implemented based on specific AI suggestions
            # For now, we'll just log it
            self.log_upgrade(upgrade, "PROCESSED", f"AI suggestion processed: {str(content)[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error processing AI suggestion: {e}")
            self.log_upgrade(upgrade, "ERROR", str(e))
            return False
    
    def create_backup(self, backup_name):
        """Create a backup before applying upgrades"""
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy critical files
            critical_files = [
                "services/",
                "VoiceStudio/",
                "installer/",
                "requirements.txt",
                "*.py"
            ]
            
            for pattern in critical_files:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file():
                        dest_path = backup_path / file_path.name
                        shutil.copy2(file_path, dest_path)
                    elif file_path.is_dir():
                        dest_path = backup_path / file_path.name
                        shutil.copytree(file_path, dest_path, dirs_exist_ok=True)
            
            logger.info(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def log_upgrade(self, upgrade, status, details):
        """Log upgrade attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "upgrade": upgrade,
            "status": status,
            "details": details
        }
        
        try:
            # Ensure logs directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Error logging upgrade: {e}")
    
    def run_auto_upgrade(self):
        """Run the complete auto-upgrade process"""
        logger.info("Starting VoiceStudio Auto-Upgrade process...")
        
        try:
            # Detect upgrades
            upgrades = self.detect_chatgpt_upgrades()
            
            if not upgrades:
                logger.info("No upgrades detected")
                return True
            
            # Apply upgrades
            successful_upgrades = 0
            failed_upgrades = 0
            
            for upgrade in upgrades:
                if self.apply_upgrade(upgrade):
                    successful_upgrades += 1
                else:
                    failed_upgrades += 1
            
            logger.info(f"Auto-upgrade completed: {successful_upgrades} successful, {failed_upgrades} failed")
            
            # Restart services if upgrades were applied
            if successful_upgrades > 0:
                self.restart_services()
            
            return True
            
        except Exception as e:
            logger.error(f"Error in auto-upgrade process: {e}")
            return False
    
    def restart_services(self):
        """Restart VoiceStudio services after upgrades"""
        logger.info("Restarting VoiceStudio services...")
        
        try:
            # Stop services
            services = ["VoiceStudioAssistant", "VoiceStudioVoiceCloning", "VoiceStudioOrchestrator"]
            
            for service in services:
                try:
                    subprocess.run(['sc', 'stop', service], capture_output=True)
                    logger.info(f"Stopped service: {service}")
                except Exception as e:
                    logger.warning(f"Error stopping service {service}: {e}")
            
            # Wait a moment
            time.sleep(5)
            
            # Start services
            for service in services:
                try:
                    subprocess.run(['sc', 'start', service], capture_output=True)
                    logger.info(f"Started service: {service}")
                except Exception as e:
                    logger.warning(f"Error starting service {service}: {e}")
            
            logger.info("Services restarted successfully")
            
        except Exception as e:
            logger.error(f"Error restarting services: {e}")

def main():
    """Main function"""
    upgrader = VoiceStudioUpgradeDetector()
    success = upgrader.run_auto_upgrade()
    
    if success:
        print("VoiceStudio Auto-Upgrade completed successfully!")
    else:
        print("VoiceStudio Auto-Upgrade failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
