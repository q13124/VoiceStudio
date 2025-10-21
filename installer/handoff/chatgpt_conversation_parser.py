#!/usr/bin/env python3
"""
VoiceStudio ChatGPT Conversation Parser
Parses ChatGPT conversations to extract upgrade instructions
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ChatGPTConversationParser:
    """Parses ChatGPT conversations to extract upgrade instructions"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.upgrades_dir = self.project_root / "upgrades"
        
    def parse_conversation(self, conversation_text):
        """Parse ChatGPT conversation to extract upgrade instructions"""
        logger.info("Parsing ChatGPT conversation for upgrade instructions...")
        
        upgrades = []
        
        # Look for code blocks with file paths
        code_pattern = r'```(?:python|bash|powershell|json|yaml|markdown)?\n(.*?)```'
        code_blocks = re.findall(code_pattern, conversation_text, re.DOTALL)
        
        for code_block in code_blocks:
            # Look for file paths in code blocks
            file_patterns = [
                r'([a-zA-Z_][a-zA-Z0-9_]*\.py)',
                r'([a-zA-Z_][a-zA-Z0-9_]*\.ps1)',
                r'([a-zA-Z_][a-zA-Z0-9_]*\.json)',
                r'([a-zA-Z_][a-zA-Z0-9_]*\.md)',
                r'([a-zA-Z_][a-zA-Z0-9_]*\.txt)'
            ]
            
            for pattern in file_patterns:
                files = re.findall(pattern, code_block)
                for file_name in files:
                    upgrades.append({
                        "type": "file_upgrade",
                        "file": file_name,
                        "content": code_block,
                        "confidence": 0.8,
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Look for upgrade instructions
        instruction_patterns = [
            r'upgrade.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)',
            r'improve.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)',
            r'fix.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)',
            r'add.*?feature.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)',
            r'enhance.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)',
            r'create.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)',
            r'update.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)'
        ]
        
        for pattern in instruction_patterns:
            matches = re.findall(pattern, conversation_text, re.IGNORECASE)
            for match in matches:
                upgrades.append({
                    "type": "instruction_upgrade",
                    "file": match,
                    "instruction": conversation_text,
                    "confidence": 0.7,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Look for package upgrade instructions
        package_patterns = [
            r'pip install.*?([a-zA-Z0-9_-]+)',
            r'install.*?package.*?([a-zA-Z0-9_-]+)',
            r'upgrade.*?package.*?([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in package_patterns:
            matches = re.findall(pattern, conversation_text, re.IGNORECASE)
            for match in matches:
                upgrades.append({
                    "type": "package_upgrade",
                    "package": match,
                    "instruction": conversation_text,
                    "confidence": 0.9,
                    "timestamp": datetime.now().isoformat()
                })
        
        logger.info(f"Extracted {len(upgrades)} upgrade instructions from conversation")
        return upgrades
    
    def save_upgrades(self, upgrades):
        """Save extracted upgrades to file"""
        if not upgrades:
            return
        
        upgrade_file = self.upgrades_dir / f"chatgpt_upgrades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(upgrade_file, 'w', encoding='utf-8') as f:
                json.dump(upgrades, f, indent=2)
            
            logger.info(f"Saved {len(upgrades)} upgrades to {upgrade_file}")
            
        except Exception as e:
            logger.error(f"Error saving upgrades: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python chatgpt_parser.py <conversation_file>")
        sys.exit(1)
    
    conversation_file = sys.argv[1]
    
    try:
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation_text = f.read()
        
        parser = ChatGPTConversationParser()
        upgrades = parser.parse_conversation(conversation_text)
        parser.save_upgrades(upgrades)
        
        print(f"Parsed {len(upgrades)} upgrade instructions from {conversation_file}")
        
    except Exception as e:
        print(f"Error parsing conversation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
