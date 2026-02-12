"""
Monitor de Performance para Sistema de Trading

Este módulo implementa monitoramento em tempo real de métricas de sistema
e performance, integrado com o sistema de logging.
"""

import psutil
import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
import json
import statistics

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class PerformanceMetrics:
    """Classe para coletar e armazenar métricas de performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.process = psutil.Process()
        
        # Buffers para histórico de métricas
        self.cpu_history = deque(maxlen=60)  # 1 minuto
        self.memory_history = deque(maxlen=60)
        self.network_history = deque(maxlen=60)
        
        # Contadores de operações
        self.operation_counts = {}
        self.operation_times = {}
        
        # Thresholds para alertas
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'memory_mb': 1024.0,
            'network_io_mb': 100.0,
            'execution_time_ms': 1000.0
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do sistema"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        process_cpu = self.process.cpu_percent()
        
        # Memória
        memory_info = self.process.memory_info()
        system_memory = psutil.virtual_memory()
        
        # Rede (se disponível)
        try:
            network_io = psutil.net_io_counters()
            network_sent_mb = network_io.bytes_sent / (1024 * 1024)
            network_recv_mb = network_io.bytes_recv / (1024 * 1024)
        except:
            network_sent_mb = 0
            network_recv_mb = 0
        
        # Disco
        try:
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        except:
            disk_read_mb = 0
            disk_write_mb = 0
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'cpu': {
                'system_percent': cpu_percent,
                'process_percent': process_cpu,
                'cores': psutil.cpu_count()
            },
            'memory': {
                'process_mb': memory_info.rss / (1024 * 1024),
                'process_percent': (memory_info.rss / system_memory.total) * 100,
                'system_percent': system_memory.percent,
                'available_mb': system_memory.available / (1024 * 1024)
            },
            'network': {
                'sent_mb': network_sent_mb,
                'recv_mb': network_recv_mb,
                'total_mb': network_sent_mb + network_recv_mb
            },
            'disk': {
                'read_mb': disk_read_mb,
                'write_mb': disk_write_mb
            }
        }
        
        # Adicionar aos históricos
        self.cpu_history.append(cpu_percent)
        self.memory_history.append(system_memory.percent)
        self.network_history.append(network_sent_mb + network_recv_mb)
        
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance com estatísticas"""
        current_metrics = self.get_system_metrics()
        
        summary = {
            'current': current_metrics,
            'averages': {},
            'peaks': {},
            'operation_stats': self.get_operation_stats()
        }
        
        # Calcular médias se temos histórico
        if self.cpu_history:
            summary['averages']['cpu_percent'] = statistics.mean(self.cpu_history)
            summary['peaks']['cpu_percent'] = max(self.cpu_history)
        
        if self.memory_history:
            summary['averages']['memory_percent'] = statistics.mean(self.memory_history)
            summary['peaks']['memory_percent'] = max(self.memory_history)
        
        if self.network_history:
            summary['averages']['network_mb'] = statistics.mean(self.network_history)
            summary['peaks']['network_mb'] = max(self.network_history)
        
        return summary
    
    def record_operation(self, operation: str, execution_time: float):
        """Registra tempo de execução de uma operação"""
        if operation not in self.operation_counts:
            self.operation_counts[operation] = 0
            self.operation_times[operation] = deque(maxlen=100)
        
        self.operation_counts[operation] += 1
        self.operation_times[operation].append(execution_time)
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das operações"""
        stats = {}
        
        for operation, times in self.operation_times.items():
            if times:
                stats[operation] = {
                    'count': self.operation_counts[operation],
                    'avg_time_ms': statistics.mean(times) * 1000,
                    'min_time_ms': min(times) * 1000,
                    'max_time_ms': max(times) * 1000,
                    'total_time_s': sum(times)
                }
                
                if len(times) > 1:
                    stats[operation]['std_dev_ms'] = statistics.stdev(times) * 1000
        
        return stats
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> list:
        """Verifica se algum threshold foi ultrapassado"""
        alerts = []
        
        # CPU
        if metrics['cpu']['system_percent'] > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'CPU_HIGH',
                'value': metrics['cpu']['system_percent'],
                'threshold': self.thresholds['cpu_percent'],
                'severity': 'WARNING'
            })
        
        # Memória
        if metrics['memory']['system_percent'] > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'MEMORY_HIGH',
                'value': metrics['memory']['system_percent'],
                'threshold': self.thresholds['memory_percent'],
                'severity': 'WARNING'
            })
        
        if metrics['memory']['process_mb'] > self.thresholds['memory_mb']:
            alerts.append({
                'type': 'PROCESS_MEMORY_HIGH',
                'value': metrics['memory']['process_mb'],
                'threshold': self.thresholds['memory_mb'],
                'severity': 'INFO'
            })
        
        return alerts


class PerformanceMonitor:
    """Monitor principal de performance com logging automático"""
    
    def __init__(self, logger, interval: int = 60, auto_start: bool = True):
        """
        Inicializa monitor de performance.
        
        Args:
            logger: Instância do TradingLogger
            interval: Intervalo em segundos para coleta automática
            auto_start: Se deve iniciar monitoramento automático
        """
        self.logger = logger
        self.interval = interval
        self.metrics = PerformanceMetrics()
        self.running = False
        self.thread = None
        
        # Callbacks para alertas
        self.alert_callbacks = []
        
        if auto_start:
            self.start()
    
    def start(self):
        """Inicia monitoramento automático"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        self.logger.info("SYSTEM", "Monitor de performance iniciado", "performance_monitor",
                        interval=self.interval, auto_logging=True)
    
    def stop(self):
        """Para monitoramento automático"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        self.logger.info("SYSTEM", "Monitor de performance parado", "performance_monitor")
    
    def _monitor_loop(self):
        """Loop principal do monitoramento"""
        while self.running:
            try:
                # Coletar métricas
                metrics = self.metrics.get_system_metrics()
                
                # Log das métricas
                self._log_performance_metrics(metrics)
                
                # Verificar alertas
                alerts = self.metrics.check_thresholds(metrics)
                for alert in alerts:
                    self._handle_alert(alert)
                
                # Chamar callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(metrics, alerts)
                    except Exception as e:
                        self.logger.error("PERFORMANCE_ERROR", f"Erro em callback: {e}", 
                                        "performance_monitor")
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.error("PERFORMANCE_ERROR", f"Erro no monitoramento: {e}", 
                                "performance_monitor")
                time.sleep(self.interval)
    
    def _log_performance_metrics(self, metrics: Dict[str, Any]):
        """Faz log das métricas de performance"""
        # Log resumido no nível PERFORMANCE
        summary_msg = (
            f"CPU: {metrics['cpu']['system_percent']:.1f}% | "
            f"RAM: {metrics['memory']['system_percent']:.1f}% | "
            f"Process: {metrics['memory']['process_mb']:.1f}MB | "
            f"Uptime: {metrics['uptime_seconds']:.0f}s"
        )
        
        self.logger.performance("CPU_USAGE", summary_msg, "performance_monitor",
                               **metrics['cpu'])
        
        # Logs detalhados em DEBUG
        self.logger.debug("MEMORY_USAGE", f"Uso de memória detalhado", "performance_monitor",
                         **metrics['memory'])
        
        self.logger.debug("NETWORK_USAGE", f"I/O de rede", "performance_monitor",
                         **metrics['network'])
    
    def _handle_alert(self, alert: Dict[str, Any]):
        """Trata alertas de performance"""
        severity = alert['severity']
        message = f"{alert['type']}: {alert['value']:.1f} (limite: {alert['threshold']:.1f})"
        
        if severity == 'WARNING':
            self.logger.warning("PERFORMANCE_WARNING", message, "performance_monitor",
                              alert_type=alert['type'], current_value=alert['value'],
                              threshold=alert['threshold'])
        else:
            self.logger.info("PERFORMANCE_INFO", message, "performance_monitor",
                           alert_type=alert['type'], current_value=alert['value'],
                           threshold=alert['threshold'])
    
    def add_alert_callback(self, callback: Callable):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def record_operation_time(self, operation: str, execution_time: float):
        """Registra tempo de execução de uma operação"""
        self.metrics.record_operation(operation, execution_time)
        
        # Log se tempo for alto
        if execution_time > 1.0:  # > 1 segundo
            self.logger.warning("EXECUTION_TIME", f"Operação lenta: {operation}", 
                              "performance_monitor", operation=operation, 
                              time_seconds=execution_time)
        elif execution_time > 0.1:  # > 100ms
            self.logger.performance("EXECUTION_TIME", f"Operação: {operation}", 
                                   "performance_monitor", operation=operation,
                                   time_ms=execution_time * 1000)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório completo de performance"""
        report = self.metrics.get_performance_summary()
        
        # Log do relatório
        self.logger.info("PERFORMANCE_REPORT", "Relatório de performance gerado", 
                        "performance_monitor", **report['current'])
        
        return report
    
    def log_operation_stats(self):
        """Faz log das estatísticas de operações"""
        stats = self.metrics.get_operation_stats()
        
        for operation, data in stats.items():
            self.logger.performance("OPERATION_STATS", f"Stats da operação: {operation}",
                                   "performance_monitor", operation=operation, **data)


def performance_timer(logger, operation_name: str = None):
    """
    Decorator para medir tempo de execução de funções.
    
    Args:
        logger: Instância do logger
        operation_name: Nome da operação (padrão: nome da função)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log de performance
                logger.performance("EXECUTION_TIME", f"Função executada: {op_name}",
                                 "performance_timer", operation=op_name,
                                 time_ms=execution_time * 1000)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error("EXECUTION_ERROR", f"Erro na execução: {op_name}",
                           "performance_timer", operation=op_name, 
                           time_ms=execution_time * 1000, exception=str(e))
                raise
        
        return wrapper
    return decorator


class PerformanceContext:
    """Context manager para medir performance de blocos de código"""
    
    def __init__(self, logger, operation_name: str, log_start: bool = False):
        self.logger = logger
        self.operation_name = operation_name
        self.log_start = log_start
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        
        if self.log_start:
            self.logger.debug("EXECUTION_START", f"Iniciando operação: {self.operation_name}",
                            "performance_context")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            # Sucesso
            self.logger.performance("EXECUTION_TIME", f"Operação concluída: {self.operation_name}",
                                   "performance_context", operation=self.operation_name,
                                   time_ms=execution_time * 1000, success=True)
        else:
            # Erro
            self.logger.error("EXECUTION_ERROR", f"Erro na operação: {self.operation_name}",
                            "performance_context", operation=self.operation_name,
                            time_ms=execution_time * 1000, exception=str(exc_val))


def setup_performance_monitoring(logger, config: Dict[str, Any] = None) -> PerformanceMonitor:
    """
    Configura e inicia monitoramento de performance.
    
    Args:
        logger: Instância do TradingLogger
        config: Configuração do monitor
    
    Returns:
        Instância do PerformanceMonitor
    """
    default_config = {
        'interval': 60,
        'auto_start': True,
        'thresholds': {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'memory_mb': 1024.0
        }
    }
    
    if config:
        default_config.update(config)
    
    monitor = PerformanceMonitor(logger, 
                               interval=default_config['interval'],
                               auto_start=default_config['auto_start'])
    
    # Configurar thresholds
    if 'thresholds' in default_config:
        monitor.metrics.thresholds.update(default_config['thresholds'])
    
    logger.info("SYSTEM", "Monitor de performance configurado", "performance_setup",
               **default_config)
    
    return monitor
