# workers/batch_processing_worker.py
# Batch processing worker for VoiceStudio

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_batch_processor import BatchProcessor, BatchJobType

class BatchProcessingWorker:
    def __init__(self, config_path=None):
        self.config_path = config_path or "config/batch_processing.json"
        self.processor = BatchProcessor(self.config_path)
        
    def create_job(self, job_type, items, configuration=None):
        """Create a batch job"""
        try:
            batch_job_type = BatchJobType(job_type)
            job_id = self.processor.create_batch_job(batch_job_type, items, configuration)
            return {"success": True, "job_id": job_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_job_status(self, job_id):
        """Get job status"""
        try:
            result = self.processor.get_job_status(job_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_job_results(self, job_id):
        """Get job results"""
        try:
            result = self.processor.get_job_results(job_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cancel_job(self, job_id):
        """Cancel a job"""
        try:
            result = self.processor.cancel_job(job_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_results(self, job_id, format="json"):
        """Export job results"""
        try:
            result = self.processor.export_results(job_id, format)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Main function for worker"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Batch Processing Worker")
    parser.add_argument("--action", choices=["create", "status", "results", "cancel", "export"], required=True,
                       help="Action to perform")
    parser.add_argument("--job-id", help="Job ID")
    parser.add_argument("--job-type", help="Job type for create action")
    parser.add_argument("--items", help="JSON file with batch items")
    parser.add_argument("--config", help="JSON file with job configuration")
    parser.add_argument("--format", choices=["json", "csv", "excel"], default="json",
                       help="Export format")
    
    args = parser.parse_args()
    
    worker = BatchProcessingWorker()
    
    if args.action == "create":
        if not args.job_type or not args.items:
            print("Error: --job-type and --items required for create action")
            sys.exit(1)
        
        # Load items
        with open(args.items, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        # Load configuration
        config = None
        if args.config:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        result = worker.create_job(args.job_type, items, config)
        print(json.dumps(result))
        
    elif args.action == "status":
        if not args.job_id:
            print("Error: --job-id required for status action")
            sys.exit(1)
        
        result = worker.get_job_status(args.job_id)
        print(json.dumps(result))
        
    elif args.action == "results":
        if not args.job_id:
            print("Error: --job-id required for results action")
            sys.exit(1)
        
        result = worker.get_job_results(args.job_id)
        print(json.dumps(result))
        
    elif args.action == "cancel":
        if not args.job_id:
            print("Error: --job-id required for cancel action")
            sys.exit(1)
        
        result = worker.cancel_job(args.job_id)
        print(json.dumps(result))
        
    elif args.action == "export":
        if not args.job_id:
            print("Error: --job-id required for export action")
            sys.exit(1)
        
        result = worker.export_results(args.job_id, args.format)
        print(json.dumps(result))

if __name__ == "__main__":
    main()
