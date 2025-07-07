"""
Performance Optimization and Model Management
Handles model quantization, batch processing, memory management, and GPU scheduling
"""

import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import json
import time
from dataclasses import dataclass
from enum import Enum
import gc
import threading
import queue
from loguru import logger
import psutil

class OptimizationLevel(Enum):
    """Optimization levels for models"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class ModelPrecision(Enum):
    """Model precision levels"""
    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    INT4 = "int4"

@dataclass
class ModelProfile:
    """Model performance profile"""
    name: str
    size_mb: float
    inference_time_ms: float
    memory_usage_mb: float
    accuracy_score: float
    optimization_level: OptimizationLevel
    precision: ModelPrecision

class ModelQuantizer:
    """Model quantization for performance optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def quantize_model(self, model: torch.nn.Module, 
                      precision: ModelPrecision = ModelPrecision.FP16) -> torch.nn.Module:
        """Quantize model to specified precision"""
        
        logger.info(f"Quantizing model to {precision.value}")
        
        if precision == ModelPrecision.FP16:
            return self._quantize_fp16(model)
        elif precision == ModelPrecision.INT8:
            return self._quantize_int8(model)
        elif precision == ModelPrecision.INT4:
            return self._quantize_int4(model)
        else:
            return model  # FP32, no quantization needed
    
    def _quantize_fp16(self, model: torch.nn.Module) -> torch.nn.Module:
        """Quantize model to FP16"""
        model = model.half()
        return model
    
    def _quantize_int8(self, model: torch.nn.Module) -> torch.nn.Module:
        """Quantize model to INT8"""
        
        # Dynamic quantization
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear, torch.nn.Conv2d},
            dtype=torch.qint8
        )
        
        return quantized_model
    
    def _quantize_int4(self, model: torch.nn.Module) -> torch.nn.Module:
        """Quantize model to INT4 (simplified implementation)"""
        
        # Note: This is a simplified implementation
        # Real INT4 quantization would require more sophisticated techniques
        logger.warning("INT4 quantization not fully implemented, using INT8")
        return self._quantize_int8(model)
    
    def benchmark_quantization(self, model: torch.nn.Module, 
                              sample_input: torch.Tensor,
                              precisions: List[ModelPrecision] = None) -> Dict[str, ModelProfile]:
        """Benchmark different quantization levels"""
        
        if precisions is None:
            precisions = [ModelPrecision.FP32, ModelPrecision.FP16, ModelPrecision.INT8]
        
        profiles = {}
        
        for precision in precisions:
            logger.info(f"Benchmarking {precision.value}")
            
            # Quantize model
            quantized_model = self.quantize_model(model.clone(), precision)
            
            # Measure performance
            profile = self._measure_model_performance(
                quantized_model, sample_input, precision
            )
            
            profiles[precision.value] = profile
        
        return profiles
    
    def _measure_model_performance(self, model: torch.nn.Module, 
                                  sample_input: torch.Tensor,
                                  precision: ModelPrecision) -> ModelProfile:
        """Measure model performance metrics"""
        
        model.eval()
        model = model.to(self.device)
        sample_input = sample_input.to(self.device)
        
        # Warm up
        with torch.no_grad():
            for _ in range(5):
                _ = model(sample_input)
        
        # Measure inference time
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(10):
                _ = model(sample_input)
        
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        end_time = time.time()
        
        avg_inference_time = (end_time - start_time) / 10 * 1000  # ms
        
        # Measure memory usage
        if torch.cuda.is_available():
            memory_usage = torch.cuda.max_memory_allocated() / 1024 / 1024  # MB
        else:
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Estimate model size
        model_size = sum(p.numel() * p.element_size() for p in model.parameters()) / 1024 / 1024  # MB
        
        return ModelProfile(
            name=f"model_{precision.value}",
            size_mb=model_size,
            inference_time_ms=avg_inference_time,
            memory_usage_mb=memory_usage,
            accuracy_score=1.0,  # Would need ground truth for real accuracy
            optimization_level=OptimizationLevel.MEDIUM,
            precision=precision
        )

class BatchProcessor:
    """Optimized batch processing for video generation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.batch_size = config.get('batch_size', 4)
        self.max_workers = config.get('max_workers', 4)
        self.memory_limit = config.get('memory_limit_gb', 8) * 1024 * 1024 * 1024  # bytes
        
    def process_batch(self, items: List[Any], 
                     processing_func: callable,
                     batch_size: Optional[int] = None) -> List[Any]:
        """Process items in optimized batches"""
        
        if batch_size is None:
            batch_size = self.batch_size
        
        results = []
        total_batches = (len(items) + batch_size - 1) // batch_size
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} (size: {len(batch)})")
            
            # Check memory before processing
            if not self._check_memory_available():
                logger.warning("Low memory, reducing batch size")
                batch_size = max(1, batch_size // 2)
                batch = batch[:batch_size]
            
            try:
                batch_results = processing_func(batch)
                results.extend(batch_results)
                
                # Clean up after batch
                self._cleanup_memory()
                
            except Exception as e:
                logger.error(f"Batch {batch_num} failed: {e}")
                # Process items individually on failure
                for item in batch:
                    try:
                        result = processing_func([item])
                        results.extend(result)
                    except Exception as item_error:
                        logger.error(f"Item processing failed: {item_error}")
                        results.append(None)
        
        return results
    
    def _check_memory_available(self) -> bool:
        """Check if sufficient memory is available"""
        
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            gpu_used = torch.cuda.memory_allocated()
            gpu_available = gpu_memory - gpu_used
            
            return gpu_available > self.memory_limit * 0.2  # 20% threshold
        else:
            ram_available = psutil.virtual_memory().available
            return ram_available > self.memory_limit * 0.2
    
    def _cleanup_memory(self):
        """Clean up memory after batch processing"""
        
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def optimize_batch_size(self, sample_items: List[Any], 
                           processing_func: callable) -> int:
        """Automatically determine optimal batch size"""
        
        optimal_batch_size = 1
        best_throughput = 0
        
        test_sizes = [1, 2, 4, 8, 16, 32]
        
        for batch_size in test_sizes:
            if batch_size > len(sample_items):
                continue
            
            try:
                # Test batch processing
                test_batch = sample_items[:batch_size]
                
                start_time = time.time()
                _ = processing_func(test_batch)
                end_time = time.time()
                
                throughput = batch_size / (end_time - start_time)
                
                logger.info(f"Batch size {batch_size}: {throughput:.2f} items/sec")
                
                if throughput > best_throughput and self._check_memory_available():
                    best_throughput = throughput
                    optimal_batch_size = batch_size
                else:
                    # Memory limit reached or performance degraded
                    break
                    
                self._cleanup_memory()
                
            except Exception as e:
                logger.warning(f"Batch size {batch_size} failed: {e}")
                break
        
        logger.info(f"Optimal batch size: {optimal_batch_size}")
        return optimal_batch_size

class MemoryManager:
    """Advanced memory management and optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory_threshold = config.get('memory_threshold', 0.8)  # 80%
        self.cleanup_frequency = config.get('cleanup_frequency', 10)  # every 10 operations
        self.operation_count = 0
        
    def monitor_memory(self):
        """Monitor system memory usage"""
        
        memory_info = {
            'system': self._get_system_memory(),
            'gpu': self._get_gpu_memory() if torch.cuda.is_available() else None,
            'process': self._get_process_memory()
        }
        
        return memory_info
    
    def _get_system_memory(self) -> Dict[str, float]:
        """Get system memory information"""
        
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / 1024**3,
            'available_gb': memory.available / 1024**3,
            'used_gb': memory.used / 1024**3,
            'percentage': memory.percent
        }
    
    def _get_gpu_memory(self) -> Dict[str, float]:
        """Get GPU memory information"""
        
        if not torch.cuda.is_available():
            return None
        
        total = torch.cuda.get_device_properties(0).total_memory
        allocated = torch.cuda.memory_allocated()
        cached = torch.cuda.memory_reserved()
        
        return {
            'total_gb': total / 1024**3,
            'allocated_gb': allocated / 1024**3,
            'cached_gb': cached / 1024**3,
            'free_gb': (total - allocated) / 1024**3
        }
    
    def _get_process_memory(self) -> Dict[str, float]:
        """Get current process memory information"""
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_gb': memory_info.rss / 1024**3,  # Resident set size
            'vms_gb': memory_info.vms / 1024**3,  # Virtual memory size
        }
    
    def check_memory_pressure(self) -> bool:
        """Check if system is under memory pressure"""
        
        system_memory = self._get_system_memory()
        
        if system_memory['percentage'] > self.memory_threshold * 100:
            return True
        
        if torch.cuda.is_available():
            gpu_memory = self._get_gpu_memory()
            gpu_usage = gpu_memory['allocated_gb'] / gpu_memory['total_gb']
            if gpu_usage > self.memory_threshold:
                return True
        
        return False
    
    def auto_cleanup(self):
        """Automatically clean up memory when needed"""
        
        self.operation_count += 1
        
        if (self.operation_count % self.cleanup_frequency == 0 or 
            self.check_memory_pressure()):
            
            logger.info("Performing memory cleanup")
            self.force_cleanup()
    
    def force_cleanup(self):
        """Force memory cleanup"""
        
        # Python garbage collection
        gc.collect()
        
        # PyTorch GPU cache cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        logger.info("Memory cleanup completed")

class GPUScheduler:
    """GPU task scheduling and optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}
        self.gpu_utilization = 0.0
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 2)
        
    def schedule_task(self, task: Dict[str, Any], priority: int = 5):
        """Schedule a GPU task"""
        
        task_id = f"task_{int(time.time() * 1000)}"
        task['id'] = task_id
        task['scheduled_time'] = time.time()
        
        self.task_queue.put((priority, task_id, task))
        logger.info(f"Scheduled task {task_id} with priority {priority}")
        
        return task_id
    
    def process_queue(self):
        """Process the GPU task queue"""
        
        while not self.task_queue.empty() and len(self.active_tasks) < self.max_concurrent_tasks:
            priority, task_id, task = self.task_queue.get()
            
            # Start task processing
            thread = threading.Thread(target=self._execute_task, args=(task,))
            thread.start()
            
            self.active_tasks[task_id] = {
                'task': task,
                'thread': thread,
                'start_time': time.time()
            }
            
            logger.info(f"Started processing task {task_id}")
    
    def _execute_task(self, task: Dict[str, Any]):
        """Execute a GPU task"""
        
        task_id = task['id']
        
        try:
            # Execute the task function
            if 'function' in task and callable(task['function']):
                result = task['function'](*task.get('args', []), **task.get('kwargs', {}))
                task['result'] = result
                task['status'] = 'completed'
                
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            task['error'] = str(e)
            task['status'] = 'failed'
        
        finally:
            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def get_gpu_utilization(self) -> float:
        """Get current GPU utilization"""
        
        if torch.cuda.is_available():
            # Simple estimation based on active tasks
            return min(len(self.active_tasks) / self.max_concurrent_tasks, 1.0)
        else:
            return 0.0
    
    def optimize_scheduling(self):
        """Optimize task scheduling based on GPU performance"""
        
        avg_task_time = self._calculate_average_task_time()
        
        # Adjust concurrent tasks based on performance
        if avg_task_time < 1.0:  # Fast tasks
            self.max_concurrent_tasks = min(self.max_concurrent_tasks + 1, 4)
        elif avg_task_time > 5.0:  # Slow tasks
            self.max_concurrent_tasks = max(self.max_concurrent_tasks - 1, 1)
        
        logger.info(f"Adjusted max concurrent tasks to {self.max_concurrent_tasks}")
    
    def _calculate_average_task_time(self) -> float:
        """Calculate average task execution time"""
        
        if not self.active_tasks:
            return 0.0
        
        current_time = time.time()
        total_time = sum(
            current_time - task_info['start_time'] 
            for task_info in self.active_tasks.values()
        )
        
        return total_time / len(self.active_tasks)

class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quantizer = ModelQuantizer(config)
        self.batch_processor = BatchProcessor(config)
        self.memory_manager = MemoryManager(config)
        self.gpu_scheduler = GPUScheduler(config)
        
        # Performance metrics
        self.metrics = {
            'total_inference_time': 0.0,
            'total_memory_used': 0.0,
            'tasks_completed': 0,
            'optimization_applied': []
        }
    
    def optimize_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entire video generation pipeline"""
        
        logger.info("Starting pipeline optimization")
        
        optimized_config = pipeline_config.copy()
        
        # Optimize models
        if 'models' in pipeline_config:
            optimized_config['models'] = self._optimize_models(pipeline_config['models'])
        
        # Optimize batch processing
        if 'batch_settings' in pipeline_config:
            optimized_config['batch_settings'] = self._optimize_batch_settings(
                pipeline_config['batch_settings']
            )
        
        # Set memory management
        optimized_config['memory_management'] = {
            'auto_cleanup': True,
            'memory_threshold': 0.8,
            'cleanup_frequency': 10
        }
        
        # Configure GPU scheduling
        optimized_config['gpu_scheduling'] = {
            'max_concurrent_tasks': 2,
            'task_priority_enabled': True
        }
        
        self.metrics['optimization_applied'].append('pipeline_optimization')
        
        return optimized_config
    
    def _optimize_models(self, models_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize model configurations"""
        
        optimized_models = {}
        
        for model_name, model_config in models_config.items():
            # Determine optimal precision based on model type
            if 'diffusion' in model_name.lower():
                optimal_precision = ModelPrecision.FP16
            elif 'tts' in model_name.lower():
                optimal_precision = ModelPrecision.FP16
            else:
                optimal_precision = ModelPrecision.FP32
            
            optimized_models[model_name] = {
                **model_config,
                'precision': optimal_precision.value,
                'quantization_enabled': True,
                'batch_size': self._determine_optimal_batch_size(model_name)
            }
        
        return optimized_models
    
    def _determine_optimal_batch_size(self, model_name: str) -> int:
        """Determine optimal batch size for model"""
        
        # Simple heuristics based on model type
        if 'diffusion' in model_name.lower():
            return 2  # Diffusion models are memory-intensive
        elif 'tts' in model_name.lower():
            return 4  # TTS models are less memory-intensive
        elif 'face' in model_name.lower():
            return 8  # Face processing can handle larger batches
        else:
            return 4  # Default batch size
    
    def _optimize_batch_settings(self, batch_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize batch processing settings"""
        
        return {
            **batch_config,
            'dynamic_batch_size': True,
            'memory_adaptive': True,
            'auto_optimization': True
        }
    
    def monitor_performance(self) -> Dict[str, Any]:
        """Monitor system performance metrics"""
        
        memory_info = self.memory_manager.monitor_memory()
        gpu_utilization = self.gpu_scheduler.get_gpu_utilization()
        
        performance_data = {
            'timestamp': time.time(),
            'memory': memory_info,
            'gpu_utilization': gpu_utilization,
            'active_tasks': len(self.gpu_scheduler.active_tasks),
            'queue_size': self.gpu_scheduler.task_queue.qsize(),
            'metrics': self.metrics
        }
        
        return performance_data
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        
        recommendations = []
        
        # Check memory usage
        memory_info = self.memory_manager.monitor_memory()
        if memory_info['system']['percentage'] > 80:
            recommendations.append("Reduce batch size to lower memory usage")
            recommendations.append("Enable model quantization to FP16")
        
        # Check GPU utilization
        gpu_util = self.gpu_scheduler.get_gpu_utilization()
        if gpu_util < 0.5:
            recommendations.append("Increase batch size to improve GPU utilization")
        elif gpu_util > 0.9:
            recommendations.append("Consider distributing tasks across multiple GPUs")
        
        # Check task queue
        if self.gpu_scheduler.task_queue.qsize() > 10:
            recommendations.append("Increase max concurrent tasks")
        
        return recommendations
    
    def apply_automatic_optimizations(self):
        """Apply automatic performance optimizations"""
        
        logger.info("Applying automatic optimizations")
        
        # Memory cleanup if under pressure
        if self.memory_manager.check_memory_pressure():
            self.memory_manager.force_cleanup()
            self.metrics['optimization_applied'].append('memory_cleanup')
        
        # Optimize GPU scheduling
        self.gpu_scheduler.optimize_scheduling()
        self.metrics['optimization_applied'].append('gpu_scheduling')
        
        # Process queued tasks
        self.gpu_scheduler.process_queue()
        
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        report = {
            'timestamp': time.time(),
            'system_info': {
                'gpu_available': torch.cuda.is_available(),
                'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'cpu_count': psutil.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total / 1024**3
            },
            'current_performance': self.monitor_performance(),
            'optimization_metrics': self.metrics,
            'recommendations': self.get_optimization_recommendations(),
            'memory_pressure': self.memory_manager.check_memory_pressure()
        }
        
        return report
