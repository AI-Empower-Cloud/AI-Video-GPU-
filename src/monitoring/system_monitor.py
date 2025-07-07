"""
AI Video GPU - Advanced Monitoring & Analytics Module
Comprehensive system monitoring, performance analytics, and optimization insights
"""

import time
import psutil
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
import threading
from dataclasses import dataclass, asdict
from loguru import logger

try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
    nvml.nvmlInit()
except ImportError:
    NVML_AVAILABLE = False
    logger.warning("NVIDIA ML not available. GPU monitoring limited.")

try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available. Metrics export limited.")

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    gpu_percent: float
    gpu_memory_percent: float
    gpu_temperature: float
    disk_io_read: int
    disk_io_write: int
    network_io_sent: int
    network_io_recv: int
    generation_fps: float
    queue_size: int
    error_count: int

@dataclass
class VideoGenerationStats:
    """Video generation statistics"""
    total_videos: int
    total_processing_time: float
    average_processing_time: float
    success_rate: float
    error_rate: float
    popular_resolutions: Dict[str, int]
    popular_durations: Dict[str, int]
    model_usage: Dict[str, int]

class SystemMonitor:
    """
    Comprehensive system monitoring for AI Video GPU
    """
    
    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Metrics storage
        self.metrics_history = deque(maxlen=3600)  # 1 hour of data
        self.performance_stats = defaultdict(list)
        
        # GPU monitoring
        self.gpu_handles = []
        if NVML_AVAILABLE:
            try:
                device_count = nvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = nvml.nvmlDeviceGetHandleByIndex(i)
                    self.gpu_handles.append(handle)
                logger.info(f"✅ Monitoring {device_count} GPU(s)")
            except Exception as e:
                logger.warning(f"GPU monitoring setup failed: {e}")
                
        # Prometheus metrics (if available)
        self.prometheus_registry = None
        self.prometheus_metrics = {}
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
            
        # Video generation tracking
        self.video_stats = {
            'total_generated': 0,
            'total_time': 0.0,
            'success_count': 0,
            'error_count': 0,
            'resolutions': defaultdict(int),
            'durations': defaultdict(int),
            'models_used': defaultdict(int)
        }
        
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics collection"""
        
        self.prometheus_registry = CollectorRegistry()
        
        self.prometheus_metrics = {
            'cpu_usage': Gauge('ai_video_gpu_cpu_usage_percent', 'CPU usage percentage', registry=self.prometheus_registry),
            'memory_usage': Gauge('ai_video_gpu_memory_usage_percent', 'Memory usage percentage', registry=self.prometheus_registry),
            'gpu_usage': Gauge('ai_video_gpu_gpu_usage_percent', 'GPU usage percentage', ['gpu_id'], registry=self.prometheus_registry),
            'gpu_memory': Gauge('ai_video_gpu_gpu_memory_percent', 'GPU memory usage percentage', ['gpu_id'], registry=self.prometheus_registry),
            'gpu_temperature': Gauge('ai_video_gpu_gpu_temperature_celsius', 'GPU temperature in Celsius', ['gpu_id'], registry=self.prometheus_registry),
            'videos_generated': Counter('ai_video_gpu_videos_total', 'Total videos generated', ['status'], registry=self.prometheus_registry),
            'processing_time': Histogram('ai_video_gpu_processing_seconds', 'Video processing time in seconds', registry=self.prometheus_registry),
            'generation_fps': Gauge('ai_video_gpu_generation_fps', 'Video generation FPS', registry=self.prometheus_registry),
            'queue_size': Gauge('ai_video_gpu_queue_size', 'Processing queue size', registry=self.prometheus_registry)
        }
        
        logger.info("✅ Prometheus metrics initialized")
        
    def start_monitoring(self):
        """Start system monitoring"""
        
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🔍 System monitoring started")
        
    def stop_monitoring(self):
        """Stop system monitoring"""
        
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
            
        logger.info("🔍 System monitoring stopped")
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Update Prometheus metrics
                if PROMETHEUS_AVAILABLE and self.prometheus_metrics:
                    self._update_prometheus_metrics(metrics)
                    
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(self.collection_interval)
                
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        
        timestamp = time.time()
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read = disk_io.read_bytes if disk_io else 0
        disk_write = disk_io.write_bytes if disk_io else 0
        
        # Network I/O
        net_io = psutil.net_io_counters()
        net_sent = net_io.bytes_sent if net_io else 0
        net_recv = net_io.bytes_recv if net_io else 0
        
        # GPU metrics
        gpu_percent = 0.0
        gpu_memory_percent = 0.0
        gpu_temperature = 0.0
        
        if NVML_AVAILABLE and self.gpu_handles:
            try:
                # Use first GPU for primary metrics
                handle = self.gpu_handles[0]
                
                # GPU utilization
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_percent = util.gpu
                
                # GPU memory
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_percent = (mem_info.used / mem_info.total) * 100
                
                # GPU temperature
                gpu_temperature = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                
            except Exception as e:
                logger.warning(f"GPU metrics collection failed: {e}")
                
        # Application-specific metrics
        generation_fps = self._calculate_generation_fps()
        queue_size = self._get_queue_size()
        error_count = self.video_stats['error_count']
        
        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            gpu_percent=gpu_percent,
            gpu_memory_percent=gpu_memory_percent,
            gpu_temperature=gpu_temperature,
            disk_io_read=disk_read,
            disk_io_write=disk_write,
            network_io_sent=net_sent,
            network_io_recv=net_recv,
            generation_fps=generation_fps,
            queue_size=queue_size,
            error_count=error_count
        )
        
    def _update_prometheus_metrics(self, metrics: PerformanceMetrics):
        """Update Prometheus metrics"""
        
        try:
            self.prometheus_metrics['cpu_usage'].set(metrics.cpu_percent)
            self.prometheus_metrics['memory_usage'].set(metrics.memory_percent)
            self.prometheus_metrics['generation_fps'].set(metrics.generation_fps)
            self.prometheus_metrics['queue_size'].set(metrics.queue_size)
            
            # GPU metrics for each GPU
            for i, handle in enumerate(self.gpu_handles):
                gpu_id = str(i)
                try:
                    util = nvml.nvmlDeviceGetUtilizationRates(handle)
                    mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                    temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                    
                    self.prometheus_metrics['gpu_usage'].labels(gpu_id=gpu_id).set(util.gpu)
                    self.prometheus_metrics['gpu_memory'].labels(gpu_id=gpu_id).set((mem_info.used / mem_info.total) * 100)
                    self.prometheus_metrics['gpu_temperature'].labels(gpu_id=gpu_id).set(temp)
                    
                except Exception as e:
                    logger.warning(f"Failed to update GPU {i} metrics: {e}")
                    
        except Exception as e:
            logger.warning(f"Prometheus metrics update failed: {e}")
            
    def _calculate_generation_fps(self) -> float:
        """Calculate video generation FPS"""
        
        # This would be updated by the video generation pipeline
        # For now, return a placeholder value
        return 0.0
        
    def _get_queue_size(self) -> int:
        """Get current processing queue size"""
        
        # This would be updated by the task queue
        # For now, return a placeholder value
        return 0
        
    def record_video_generation(
        self,
        processing_time: float,
        success: bool,
        resolution: str = "1920x1080",
        duration: float = 0.0,
        model_used: str = "default"
    ):
        """Record video generation statistics"""
        
        self.video_stats['total_generated'] += 1
        self.video_stats['total_time'] += processing_time
        
        if success:
            self.video_stats['success_count'] += 1
        else:
            self.video_stats['error_count'] += 1
            
        self.video_stats['resolutions'][resolution] += 1
        self.video_stats['durations'][f"{int(duration)}s"] += 1
        self.video_stats['models_used'][model_used] += 1
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE and self.prometheus_metrics:
            status = 'success' if success else 'error'
            self.prometheus_metrics['videos_generated'].labels(status=status).inc()
            self.prometheus_metrics['processing_time'].observe(processing_time)
            
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        
        if not self.metrics_history:
            return {}
            
        latest = self.metrics_history[-1]
        return asdict(latest)
        
    def get_metrics_history(self, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics history for specified duration"""
        
        cutoff_time = time.time() - (duration_minutes * 60)
        
        filtered_metrics = [
            asdict(m) for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        return filtered_metrics
        
    def get_video_generation_stats(self) -> VideoGenerationStats:
        """Get video generation statistics"""
        
        total = self.video_stats['total_generated']
        success_rate = (self.video_stats['success_count'] / total * 100) if total > 0 else 0
        error_rate = (self.video_stats['error_count'] / total * 100) if total > 0 else 0
        avg_time = (self.video_stats['total_time'] / total) if total > 0 else 0
        
        return VideoGenerationStats(
            total_videos=total,
            total_processing_time=self.video_stats['total_time'],
            average_processing_time=avg_time,
            success_rate=success_rate,
            error_rate=error_rate,
            popular_resolutions=dict(self.video_stats['resolutions']),
            popular_durations=dict(self.video_stats['durations']),
            model_usage=dict(self.video_stats['models_used'])
        )
        
    def get_performance_insights(self) -> Dict[str, Any]:
        """Generate performance insights and recommendations"""
        
        if len(self.metrics_history) < 10:
            return {'message': 'Insufficient data for insights'}
            
        recent_metrics = list(self.metrics_history)[-60:]  # Last 60 data points
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_gpu = sum(m.gpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_gpu_memory = sum(m.gpu_memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_gpu_temp = sum(m.gpu_temperature for m in recent_metrics) / len(recent_metrics)
        
        insights = {
            'system_health': 'good',
            'recommendations': [],
            'warnings': [],
            'averages': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory,
                'gpu_percent': avg_gpu,
                'gpu_memory_percent': avg_gpu_memory,
                'gpu_temperature': avg_gpu_temp
            }
        }
        
        # Generate recommendations
        if avg_cpu > 80:
            insights['recommendations'].append("High CPU usage detected. Consider reducing concurrent processing or upgrading CPU.")
            insights['system_health'] = 'warning'
            
        if avg_memory > 85:
            insights['recommendations'].append("High memory usage detected. Consider reducing batch size or adding more RAM.")
            insights['system_health'] = 'warning'
            
        if avg_gpu > 90:
            insights['recommendations'].append("GPU at high utilization. This is good for performance but monitor for thermal throttling.")
            
        if avg_gpu_memory > 90:
            insights['recommendations'].append("GPU memory usage high. Consider reducing model size or batch size.")
            insights['system_health'] = 'warning'
            
        if avg_gpu_temp > 80:
            insights['warnings'].append(f"GPU temperature high ({avg_gpu_temp:.1f}°C). Check cooling.")
            insights['system_health'] = 'critical'
            
        if avg_gpu_temp > 85:
            insights['warnings'].append("Critical GPU temperature! Risk of thermal throttling.")
            insights['system_health'] = 'critical'
            
        # Performance optimization suggestions
        video_stats = self.get_video_generation_stats()
        if video_stats.error_rate > 10:
            insights['recommendations'].append(f"High error rate ({video_stats.error_rate:.1f}%). Check system stability and model configuration.")
            
        if video_stats.average_processing_time > 120:  # More than 2 minutes
            insights['recommendations'].append("Slow processing times detected. Consider GPU optimization or model tuning.")
            
        return insights
        
    def export_metrics(self, filepath: str, format: str = "json"):
        """Export metrics to file"""
        
        data = {
            'export_time': datetime.now().isoformat(),
            'metrics_history': [asdict(m) for m in self.metrics_history],
            'video_stats': asdict(self.get_video_generation_stats()),
            'performance_insights': self.get_performance_insights()
        }
        
        filepath = Path(filepath)
        
        if format.lower() == "json":
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif format.lower() == "csv":
            import pandas as pd
            df = pd.DataFrame([asdict(m) for m in self.metrics_history])
            df.to_csv(filepath, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        logger.info(f"Metrics exported to {filepath}")
        
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        
        if not PROMETHEUS_AVAILABLE or not self.prometheus_registry:
            return "Prometheus not available"
            
        from prometheus_client import generate_latest
        return generate_latest(self.prometheus_registry).decode()

class AlertManager:
    """
    Alert management system for monitoring critical system states
    """
    
    def __init__(self, monitor: SystemMonitor):
        self.monitor = monitor
        self.alert_rules = []
        self.active_alerts = {}
        self.alert_history = []
        
        # Default alert rules
        self._setup_default_alerts()
        
    def _setup_default_alerts(self):
        """Setup default alerting rules"""
        
        self.alert_rules = [
            {
                'name': 'high_gpu_temperature',
                'condition': lambda m: m.gpu_temperature > 85,
                'severity': 'critical',
                'message': 'GPU temperature critically high: {gpu_temperature}°C'
            },
            {
                'name': 'high_memory_usage',
                'condition': lambda m: m.memory_percent > 90,
                'severity': 'warning',
                'message': 'High memory usage: {memory_percent}%'
            },
            {
                'name': 'high_gpu_memory',
                'condition': lambda m: m.gpu_memory_percent > 95,
                'severity': 'critical',
                'message': 'GPU memory critically high: {gpu_memory_percent}%'
            },
            {
                'name': 'processing_errors',
                'condition': lambda m: m.error_count > 10,
                'severity': 'warning',
                'message': 'High error count: {error_count} errors'
            }
        ]
        
    def check_alerts(self):
        """Check all alert rules against current metrics"""
        
        if not self.monitor.metrics_history:
            return
            
        latest_metrics = self.monitor.metrics_history[-1]
        
        for rule in self.alert_rules:
            alert_name = rule['name']
            
            if rule['condition'](latest_metrics):
                # Alert condition met
                if alert_name not in self.active_alerts:
                    # New alert
                    alert = {
                        'name': alert_name,
                        'severity': rule['severity'],
                        'message': rule['message'].format(**asdict(latest_metrics)),
                        'triggered_at': time.time(),
                        'metrics': asdict(latest_metrics)
                    }
                    
                    self.active_alerts[alert_name] = alert
                    self.alert_history.append(alert.copy())
                    
                    logger.warning(f"🚨 ALERT: {alert['message']}")
                    
            else:
                # Alert condition not met
                if alert_name in self.active_alerts:
                    # Alert resolved
                    resolved_alert = self.active_alerts.pop(alert_name)
                    resolved_alert['resolved_at'] = time.time()
                    resolved_alert['duration'] = resolved_alert['resolved_at'] - resolved_alert['triggered_at']
                    
                    logger.info(f"✅ RESOLVED: {alert_name} (duration: {resolved_alert['duration']:.1f}s)")
                    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
        
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for specified hours"""
        
        cutoff_time = time.time() - (hours * 3600)
        
        return [
            alert for alert in self.alert_history
            if alert['triggered_at'] >= cutoff_time
        ]
