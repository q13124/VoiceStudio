#!/usr/bin/env python3
"""
VoiceStudio Performance Optimization Script
Monitors system performance and provides optimization recommendations.
"""

import psutil
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Any
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and provide optimization recommendations"""
    
    def __init__(self):
        self.metrics = {}
        self.recommendations = []
        self._running = False
        self._monitor_thread = None
        self._metrics_queue = queue.Queue()
    
    def start_monitoring(self, interval: int = 30):
        """Start performance monitoring"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,), 
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"Performance monitoring started with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self._running:
            try:
                metrics = self._collect_metrics()
                self._analyze_performance(metrics)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': processes[:10]  # Top 10 processes
            }
            
            self.metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}
    
    def _analyze_performance(self, metrics: Dict[str, Any]):
        """Analyze performance metrics and generate recommendations"""
        recommendations = []
        
        # CPU analysis
        if metrics.get('cpu', {}).get('percent', 0) > 80:
            recommendations.append({
                'type': 'cpu',
                'severity': 'high',
                'message': 'High CPU usage detected',
                'recommendation': 'Consider optimizing CPU-intensive operations or scaling horizontally'
            })
        elif metrics.get('cpu', {}).get('percent', 0) > 60:
            recommendations.append({
                'type': 'cpu',
                'severity': 'medium',
                'message': 'Moderate CPU usage',
                'recommendation': 'Monitor CPU usage and consider optimization'
            })
        
        # Memory analysis
        memory_percent = metrics.get('memory', {}).get('percent', 0)
        if memory_percent > 90:
            recommendations.append({
                'type': 'memory',
                'severity': 'high',
                'message': 'Critical memory usage',
                'recommendation': 'Immediate memory optimization required. Consider increasing RAM or optimizing memory usage'
            })
        elif memory_percent > 80:
            recommendations.append({
                'type': 'memory',
                'severity': 'medium',
                'message': 'High memory usage',
                'recommendation': 'Monitor memory usage and consider optimization'
            })
        
        # Disk analysis
        disk_percent = metrics.get('disk', {}).get('percent', 0)
        if disk_percent > 90:
            recommendations.append({
                'type': 'disk',
                'severity': 'high',
                'message': 'Critical disk usage',
                'recommendation': 'Immediate disk cleanup required. Consider archiving old data'
            })
        elif disk_percent > 80:
            recommendations.append({
                'type': 'disk',
                'severity': 'medium',
                'message': 'High disk usage',
                'recommendation': 'Monitor disk usage and consider cleanup'
            })
        
        # Swap analysis
        swap_percent = metrics.get('swap', {}).get('percent', 0)
        if swap_percent > 50:
            recommendations.append({
                'type': 'swap',
                'severity': 'high',
                'message': 'High swap usage',
                'recommendation': 'High swap usage indicates memory pressure. Consider increasing RAM'
            })
        
        self.recommendations = recommendations
        
        # Log recommendations
        for rec in recommendations:
            if rec['severity'] == 'high':
                logger.warning(f"Performance Alert: {rec['message']} - {rec['recommendation']}")
            elif rec['severity'] == 'medium':
                logger.info(f"Performance Notice: {rec['message']} - {rec['recommendation']}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'platform': psutil.WINDOWS if hasattr(psutil, 'WINDOWS') else 'unknown',
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total
            }
        }
    
    def get_optimization_suggestions(self) -> List[Dict[str, str]]:
        """Get specific optimization suggestions for VoiceStudio"""
        suggestions = []
        
        # Database optimizations
        suggestions.append({
            'category': 'Database',
            'suggestion': 'Enable connection pooling and async operations',
            'impact': 'High',
            'implementation': 'Already implemented in optimized database.py'
        })
        
        suggestions.append({
            'category': 'Database',
            'suggestion': 'Add database indexes for frequently queried columns',
            'impact': 'High',
            'implementation': 'Already implemented in optimized database.py'
        })
        
        # Service discovery optimizations
        suggestions.append({
            'category': 'Service Discovery',
            'suggestion': 'Implement parallel health checks',
            'impact': 'Medium',
            'implementation': 'Already implemented in optimized service_discovery.py'
        })
        
        suggestions.append({
            'category': 'Service Discovery',
            'suggestion': 'Add HTTP session pooling',
            'impact': 'Medium',
            'implementation': 'Already implemented in optimized service_discovery.py'
        })
        
        # Audio processing optimizations
        suggestions.append({
            'category': 'Audio Processing',
            'suggestion': 'Implement parallel audio processing',
            'impact': 'High',
            'implementation': 'Already implemented in optimized audio_processor.py'
        })
        
        suggestions.append({
            'category': 'Audio Processing',
            'suggestion': 'Add file metadata caching',
            'impact': 'Medium',
            'implementation': 'Already implemented in optimized audio_processor.py'
        })
        
        # General optimizations
        suggestions.append({
            'category': 'General',
            'suggestion': 'Use async/await for I/O operations',
            'impact': 'High',
            'implementation': 'Consider migrating HTTP handlers to async'
        })
        
        suggestions.append({
            'category': 'General',
            'suggestion': 'Implement request/response caching',
            'impact': 'Medium',
            'implementation': 'Add Redis or in-memory caching layer'
        })
        
        suggestions.append({
            'category': 'General',
            'suggestion': 'Use connection pooling for external services',
            'impact': 'Medium',
            'implementation': 'Implement HTTP connection pooling'
        })
        
        return suggestions

def main():
    """Main function for performance monitoring"""
    monitor = PerformanceMonitor()
    
    try:
        # Start monitoring
        monitor.start_monitoring(interval=30)
        
        # Run for a while to collect data
        time.sleep(60)
        
        # Generate report
        report = monitor.get_performance_report()
        print("\n=== Performance Report ===")
        print(json.dumps(report, indent=2))
        
        # Get optimization suggestions
        suggestions = monitor.get_optimization_suggestions()
        print("\n=== Optimization Suggestions ===")
        for suggestion in suggestions:
            print(f"\n{suggestion['category']}: {suggestion['suggestion']}")
            print(f"Impact: {suggestion['impact']}")
            print(f"Implementation: {suggestion['implementation']}")
        
    except KeyboardInterrupt:
        logger.info("Performance monitoring interrupted by user")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
