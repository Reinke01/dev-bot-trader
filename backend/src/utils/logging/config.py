"""
Gerenciador de configuração do sistema de logging.

Carrega e valida configurações com type-safety.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .models import LogConfig, HandlerConfig, PYDANTIC_AVAILABLE
from .enums import LogLevel


class ConfigManager:
    """
    Gerencia configuração do sistema de logging.
    
    Suporta carregar de arquivo JSON ou usar configuração padrão.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa gerenciador de configuração.
        
        Args:
            config_path: Caminho para arquivo de configuração JSON (opcional)
        """
        self.config_path = config_path
        self._config: Optional[LogConfig] = None
    
    def load(self) -> LogConfig:
        """
        Carrega configuração de arquivo ou retorna padrão.
        
        Returns:
            LogConfig carregado
        """
        if self._config is not None:
            return self._config
        
        # Tentar carregar de arquivo
        if self.config_path and os.path.exists(self.config_path):
            try:
                self._config = self._load_from_file(self.config_path)
                return self._config
            except Exception as e:
                print(f"⚠️ Erro ao carregar configuração de {self.config_path}: {e}")
                print("Usando configuração padrão...")
        
        # Usar configuração padrão
        self._config = LogConfig.default()
        return self._config
    
    def _load_from_file(self, filepath: str) -> LogConfig:
        """
        Carrega configuração de arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            LogConfig carregado
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Converter para LogConfig
        if PYDANTIC_AVAILABLE:
            return LogConfig.from_dict(data)
        else:
            # Parse manual para dataclass
            return self._parse_config_dict(data)
    
    def _parse_config_dict(self, data: Dict[str, Any]) -> LogConfig:
        """
        Parse manual de dicionário para LogConfig (fallback sem Pydantic).
        
        Args:
            data: Dicionário com configuração
            
        Returns:
            LogConfig criado
        """
        # Extrair handlers se presentes
        handlers = {}
        if 'handlers' in data:
            for name, handler_data in data['handlers'].items():
                handlers[name] = HandlerConfig(**handler_data)
        
        # Criar LogConfig
        return LogConfig(
            log_level=data.get('log_level', 'DEBUG'),
            console_enabled=data.get('console_enabled', True),
            console_level=data.get('console_level', 'DEBUG'),
            master_file_enabled=data.get('master_file_enabled', True),
            master_file_path=data.get('master_file_path', 'logs/master/trading_bot_{date}.log'),
            master_file_level=data.get('master_file_level', 'DEBUG'),
            telegram_enabled=data.get('telegram_enabled', False),
            telegram_categories=data.get('telegram_categories', []),
            handlers=handlers
        )
    
    def save(self, filepath: Optional[str] = None) -> None:
        """
        Salva configuração atual em arquivo.
        
        Args:
            filepath: Caminho para salvar (usa config_path se None)
        """
        if self._config is None:
            raise ValueError("Nenhuma configuração carregada para salvar")
        
        save_path = filepath or self.config_path
        if not save_path:
            raise ValueError("Nenhum caminho especificado para salvar configuração")
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Converter para dicionário
        if PYDANTIC_AVAILABLE:
            data = self._config.model_dump()
        else:
            data = self._config_to_dict(self._config)
        
        # Salvar JSON
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _config_to_dict(self, config: LogConfig) -> Dict[str, Any]:
        """
        Converte LogConfig para dicionário (fallback sem Pydantic).
        
        Args:
            config: LogConfig a converter
            
        Returns:
            Dicionário com configuração
        """
        from dataclasses import asdict
        return asdict(config)
    
    def get_level_value(self, level_name: str) -> int:
        """
        Converte nome de nível para valor inteiro.
        
        Args:
            level_name: Nome do nível (DEBUG, INFO, etc)
            
        Returns:
            Valor inteiro do nível
        """
        try:
            return LogLevel[level_name.upper()].value
        except KeyError:
            # Fallback para INFO
            return LogLevel.INFO.value
    
    @property
    def config(self) -> LogConfig:
        """Retorna configuração atual (carrega se necessário)."""
        if self._config is None:
            return self.load()
        return self._config


def load_config(config_path: Optional[str] = None) -> LogConfig:
    """
    Função de conveniência para carregar configuração.
    
    Args:
        config_path: Caminho para arquivo de configuração
        
    Returns:
        LogConfig carregado
    """
    manager = ConfigManager(config_path)
    return manager.load()

