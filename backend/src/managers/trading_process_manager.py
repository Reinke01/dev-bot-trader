import streamlit as st
import subprocess
import psutil
import json
import os
import sys
from datetime import datetime
from typing import Dict, List
import threading
from collections import deque

# Adicionar o diretório pai ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TradingProcessManager:
    def __init__(self):
        self.processes: Dict[int, Dict] = {}
        self.process_logs: Dict[int, deque] = {}
        self.config_file = "trading_processes.json"
        self.load_config()
    
    def load_config(self):
        """Carrega configurações salvas dos processos"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_processes = json.load(f)
                    # Converter chaves de string para int (JSON sempre converte chaves numéricas para strings)
                    self.processes = {int(k): v for k, v in loaded_processes.items()}
            except:
                self.processes = {}
    
    def save_config(self):
        """Salva configurações dos processos"""
        with open(self.config_file, 'w') as f:
            json.dump(self.processes, f, indent=2)
    
    def start_process(self, strategy_name: str, script_path: str, args: List[str] = None, config: Dict = None) -> int:
        """Inicia um novo processo de trading"""
        cmd = ['python', script_path]
        if args:
            cmd.extend(args)
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        process_id = process.pid
        self.processes[process_id] = {
            'strategy_name': strategy_name,
            'script': script_path,
            'args': args or [],
            'config': config or {},
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'pid': process_id
        }
        
        # Inicializar deque de logs para este processo
        self.process_logs[process_id] = deque(maxlen=1000)
        
        # Thread para capturar logs
        def capture_logs():
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    self.process_logs[process_id].append({
                        'timestamp': datetime.now().isoformat(),
                        'message': line.strip()
                    })
        
        log_thread = threading.Thread(target=capture_logs, daemon=True)
        log_thread.start()
        
        self.save_config()
        return process_id
    
    def stop_process(self, process_id) -> bool:
        """Para um processo específico"""
        try:
            # Garantir que process_id seja um inteiro
            if isinstance(process_id, str):
                process_id = int(process_id)
            
            if process_id in self.processes:
                # Tentar terminar o processo
                process = psutil.Process(process_id)
                process.terminate()
                
                # Aguardar um pouco e forçar kill se necessário
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    process.kill()
                
                self.processes[process_id]['status'] = 'stopped'
                self.processes[process_id]['end_time'] = datetime.now().isoformat()
                self.save_config()
                return True
        except (psutil.NoSuchProcess, ValueError, TypeError):
            pass
        except Exception as e:
            st.error(f"Erro ao parar processo {process_id}: {e}")
        
        return False
    
    def restart_process(self, process_id) -> bool:
        """Reinicia um processo"""
        try:
            # Garantir que process_id seja um inteiro
            if isinstance(process_id, str):
                process_id = int(process_id)
            
            if process_id in self.processes:
                process_info = self.processes[process_id]
                
                # Parar processo atual
                self.stop_process(process_id)
                
                # Remover processo antigo do dicionário e salvar
                del self.processes[process_id]
                self.save_config()
                
                # Iniciar novo processo com mesma configuração
                new_pid = self.start_process(
                    process_info['strategy_name'],
                    process_info['script'],
                    process_info['args'],
                    process_info['config']
                )
                
                return new_pid
        except (ValueError, TypeError):
            pass
        return False
    
    def get_process_status(self, process_id) -> str:
        """Obtém status atual do processo"""
        try:
            # Garantir que process_id seja um inteiro
            if isinstance(process_id, str):
                process_id = int(process_id)
            
            process = psutil.Process(process_id)
            if process.is_running():
                return 'running'
            else:
                return 'stopped'
        except (psutil.NoSuchProcess, ValueError, TypeError):
            return 'stopped'
    
    def get_logs(self, process_id, max_lines: int = 50) -> List[Dict]:
        """Obtém logs de um processo específico"""
        try:
            # Garantir que process_id seja um inteiro
            if isinstance(process_id, str):
                process_id = int(process_id)
            
            if process_id in self.process_logs:
                # Retornar os últimos N logs (não remove do deque)
                return list(self.process_logs[process_id])[-max_lines:]
            
        except (ValueError, TypeError):
            pass
        return []
    
    def clear_logs(self, process_id) -> bool:
        """Limpa os logs de um processo específico"""
        try:
            if isinstance(process_id, str):
                process_id = int(process_id)
            
            if process_id in self.process_logs:
                self.process_logs[process_id].clear()
                return True
        except (ValueError, TypeError):
            pass
        return False