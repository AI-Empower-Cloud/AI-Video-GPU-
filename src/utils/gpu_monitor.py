"""
GPU Monitoring and Performance Utilities
Track GPU usage, memory, and optimize performance
"""

import time
import psutil
from typing import Dict, List, Optional
from loguru import logger
import threading
import torch

class GPUMonitor:
    """
    GPU performance monitoring and optimization
    Tracks memory usage, temperature, and performance metrics
    """
    
    def __init__(self):
        self.monitoring = False
        self.stats_history = []
        self.monitor_thread = None
        
        # Check available monitoring tools
        self.nvidia_ml_available = self._check_nvidia_ml()
        self.torch_available = torch.cuda.is_available()
        
    def _check_nvidia_ml(self) -> bool:
        """Check if nvidia-ml-py is available"""
        try:
            import pynvml
            pynvml.nvmlInit()
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous GPU monitoring"""
        if self.monitoring:
            logger.warning("GPU monitoring already active")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("GPU monitoring started")
    
    def stop_monitoring(self):
        """Stop GPU monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("GPU monitoring stopped")
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                stats = self.get_current_stats()
                self.stats_history.append({
                    'timestamp': time.time(),
                    **stats
                })
                
                # Keep only last 1000 entries
                if len(self.stats_history) > 1000:
                    self.stats_history = self.stats_history[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def get_current_stats(self) -> Dict:
        """Get current GPU statistics"""
        stats = {
            'gpu_available': False,
            'gpu_count': 0,
            'memory_used': 0,
            'memory_total': 0,
            'memory_percent': 0,
            'temperature': 0,
            'utilization': 0,
            'power_usage': 0
        }
        
        try:
            if self.torch_available:
                stats['gpu_available'] = True
                stats['gpu_count'] = torch.cuda.device_count()
                
                # Get memory info for primary GPU
                if stats['gpu_count'] > 0:
                    memory_info = torch.cuda.memory_stats(0)
                    stats['memory_used'] = memory_info.get('allocated_bytes.all.current', 0)
                    stats['memory_total'] = torch.cuda.get_device_properties(0).total_memory
                    stats['memory_percent'] = (stats['memory_used'] / stats['memory_total']) * 100
            
            # Get additional stats from nvidia-ml if available
            if self.nvidia_ml_available:
                nvidia_stats = self._get_nvidia_stats()
                stats.update(nvidia_stats)
            
            # Get system memory and CPU
            system_stats = self._get_system_stats()
            stats.update(system_stats)
            
        except Exception as e:
            logger.error(f"Error getting GPU stats: {e}")
        
        return stats
    
    def _get_nvidia_stats(self) -> Dict:
        """Get detailed stats from NVIDIA Management Library"""
        stats = {}
        
        try:
            import pynvml
            
            # Get handle for first GPU
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # Temperature
            try:
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                stats['temperature'] = temp
            except:
                pass
            
            # Utilization
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                stats['utilization'] = util.gpu
            except:
                pass
            
            # Power usage
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                stats['power_usage'] = power
            except:
                pass
            
            # Memory info (more detailed)
            try:
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                stats['memory_used'] = mem_info.used
                stats['memory_total'] = mem_info.total
                stats['memory_percent'] = (mem_info.used / mem_info.total) * 100
            except:
                pass
            
        except Exception as e:
            logger.debug(f"NVIDIA-ML stats unavailable: {e}")
        
        return stats
    
    def _get_system_stats(self) -> Dict:
        """Get system-level performance stats"""
        stats = {}
        
        try:
            # CPU usage
            stats['cpu_percent'] = psutil.cpu_percent(interval=None)
            
            # System memory
            memory = psutil.virtual_memory()
            stats['system_memory_used'] = memory.used
            stats['system_memory_total'] = memory.total
            stats['system_memory_percent'] = memory.percent
            
            # Disk usage for current directory
            disk = psutil.disk_usage('.')
            stats['disk_used'] = disk.used
            stats['disk_total'] = disk.total
            stats['disk_percent'] = (disk.used / disk.total) * 100
            
        except Exception as e:
            logger.debug(f"System stats error: {e}")
        
        return stats
    
    def get_stats(self) -> Dict:
        """Get current comprehensive stats"""
        return self.get_current_stats()
    
    def get_stats_history(self, duration_minutes: float = 5.0) -> List[Dict]:
        """Get recent stats history"""
        cutoff_time = time.time() - (duration_minutes * 60)
        return [
            stats for stats in self.stats_history
            if stats['timestamp'] > cutoff_time
        ]
    
    def optimize_memory(self):
        """Optimize GPU memory usage"""
        logger.info("Optimizing GPU memory...")
        
        try:
            if self.torch_available:
                # Clear PyTorch cache
                torch.cuda.empty_cache()
                
                # Force garbage collection
                import gc
                gc.collect()
                
                logger.info("GPU memory optimization completed")
            else:
                logger.warning("No GPU available for optimization")
                
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
    
    def check_memory_requirements(self, required_mb: int) -> bool:
        """Check if enough GPU memory is available"""
        stats = self.get_current_stats()
        
        if not stats['gpu_available']:
            return False
        
        available_mb = (stats['memory_total'] - stats['memory_used']) / (1024 * 1024)
        
        logger.info(f"Required: {required_mb}MB, Available: {available_mb:.1f}MB")
        
        return available_mb >= required_mb
    
    def suggest_optimizations(self) -> List[str]:
        """Suggest performance optimizations based on current stats"""
        suggestions = []
        stats = self.get_current_stats()
        
        # GPU memory suggestions
        if stats.get('memory_percent', 0) > 90:
            suggestions.append("GPU memory usage is very high (>90%). Consider reducing batch size or model size.")
        elif stats.get('memory_percent', 0) > 75:
            suggestions.append("GPU memory usage is high (>75%). Monitor for potential out-of-memory errors.")
        
        # Temperature suggestions
        if stats.get('temperature', 0) > 80:
            suggestions.append("GPU temperature is high (>80°C). Check cooling and reduce workload if necessary.")
        
        # System memory suggestions
        if stats.get('system_memory_percent', 0) > 90:
            suggestions.append("System RAM usage is very high (>90%). Close unnecessary applications.")
        
        # CPU suggestions
        if stats.get('cpu_percent', 0) > 90:
            suggestions.append("CPU usage is very high (>90%). This may bottleneck GPU performance.")
        
        # Disk space suggestions
        if stats.get('disk_percent', 0) > 90:
            suggestions.append("Disk space is low (<10% free). This may affect temporary file operations.")
        
        # Performance suggestions
        if not stats.get('gpu_available', False):
            suggestions.append("No GPU detected. Performance will be significantly slower on CPU.")
        
        if len(suggestions) == 0:
            suggestions.append("System performance looks good!")
        
        return suggestions
    
    def benchmark_gpu(self, duration: float = 10.0) -> Dict:
        """Run a simple GPU benchmark"""
        logger.info(f"Running GPU benchmark for {duration}s...")
        
        if not self.torch_available:
            return {'error': 'No GPU available for benchmarking'}
        
        try:
            # Start monitoring
            start_time = time.time()
            initial_stats = self.get_current_stats()
            
            # Run compute-intensive operations
            device = torch.device('cuda')
            
            # Matrix multiplication benchmark
            matrix_size = 2048
            matrices_computed = 0
            
            end_time = start_time + duration
            while time.time() < end_time:
                a = torch.randn(matrix_size, matrix_size, device=device)
                b = torch.randn(matrix_size, matrix_size, device=device)
                c = torch.mm(a, b)
                matrices_computed += 1
                
                # Prevent memory overflow
                if matrices_computed % 10 == 0:
                    torch.cuda.empty_cache()
            
            # Get final stats
            final_stats = self.get_current_stats()
            
            # Calculate performance metrics
            actual_duration = time.time() - start_time
            operations_per_second = matrices_computed / actual_duration
            
            benchmark_results = {
                'duration': actual_duration,
                'operations_completed': matrices_computed,
                'operations_per_second': operations_per_second,
                'matrix_size': matrix_size,
                'initial_memory_mb': initial_stats['memory_used'] / (1024 * 1024),
                'final_memory_mb': final_stats['memory_used'] / (1024 * 1024),
                'peak_temperature': final_stats.get('temperature', 0),
                'average_utilization': final_stats.get('utilization', 0)
            }
            
            logger.success(f"Benchmark completed: {operations_per_second:.1f} ops/sec")
            return benchmark_results
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return {'error': str(e)}
        
        finally:
            # Cleanup
            torch.cuda.empty_cache()
    
    def export_stats(self, filepath: str, duration_minutes: float = 60.0):
        """Export performance stats to file"""
        try:
            import json
            
            stats_data = {
                'export_timestamp': time.time(),
                'duration_minutes': duration_minutes,
                'current_stats': self.get_current_stats(),
                'history': self.get_stats_history(duration_minutes),
                'suggestions': self.suggest_optimizations()
            }
            
            with open(filepath, 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            logger.info(f"Performance stats exported to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export stats: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_monitoring()
