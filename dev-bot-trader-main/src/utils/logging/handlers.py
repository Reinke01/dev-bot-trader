"""
Handlers de log refatorados e simplificados.

Remove complexidade desnecessária mantendo funcionalidades essenciais.
"""

import logging
import logging.handlers
import os
import glob
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Set

from .models import LogEvent
from .enums import LogCategory


class FileHandlerFactory:
    """
    Factory para criar handlers de arquivo com rotação.
    
    Simplifica criação de handlers e garante que diretórios existam.
    """
    
    @staticmethod
    def create_rotating_handler(
        filepath: str,
        level: int = logging.DEBUG,
        formatter: Optional[logging.Formatter] = None,
        when: str = 'midnight',
        backup_count: int = 30
    ) -> logging.Handler:
        """
        Cria handler com rotação de arquivos.
        
        Args:
            filepath: Caminho do arquivo (pode conter {date})
            level: Nível do handler
            formatter: Formatador a usar
            when: Quando rodar (midnight, etc)
            backup_count: Quantos backups manter
            
        Returns:
            Handler configurado
        """
        # Expandir {date} no path
        if '{date}' in filepath:
            today = datetime.now().strftime("%Y-%m-%d")
            filepath = filepath.replace('{date}', today)
        
        # Garantir que diretório existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Criar handler
        handler = logging.handlers.TimedRotatingFileHandler(
            filepath,
            when=when,
            interval=1,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        handler.setLevel(level)
        
        if formatter:
            handler.setFormatter(formatter)
        
        return handler
    
    @staticmethod
    def create_daily_date_handler(
        filepath_pattern: str,
        level: int = logging.DEBUG,
        formatter: Optional[logging.Formatter] = None,
        backup_count: int = 30
    ) -> logging.Handler:
        """
        Cria handler que gera arquivo novo por dia com data no nome.
        Resolve o problema de nome incorreto quando bot roda 24/7.
        
        Args:
            filepath_pattern: Path com {date} (ex: "logs/bot_{date}.log")
            level: Nível do handler
            formatter: Formatador a usar
            backup_count: Dias a manter
            
        Returns:
            DailyDateFileHandler configurado
        """
        handler = DailyDateFileHandler(
            filepath_pattern=filepath_pattern,
            level=level,
            formatter=formatter,
            backup_count=backup_count
        )
        
        return handler


class DailyDateFileHandler(logging.Handler):
    """
    Handler que cria arquivo novo por dia com data correta no nome.
    
    Diferente do TimedRotatingFileHandler, este handler:
    - Sempre usa a data ATUAL no nome do arquivo
    - Fecha o arquivo antigo e cria novo à meia-noite
    - Funciona corretamente com bot rodando 24/7
    - Thread-safe para múltiplos bots/threads
    """
    
    def __init__(
        self,
        filepath_pattern: str,  # Ex: "logs/master/trading_bot_{date}.log"
        level: int = logging.DEBUG,
        formatter: Optional[logging.Formatter] = None,
        backup_count: int = 30,
        encoding: str = 'utf-8'
    ):
        """
        Inicializa handler com rotação diária por data.
        
        Args:
            filepath_pattern: Caminho com {date} para substituir
            level: Nível do handler
            formatter: Formatador a usar
            backup_count: Quantos dias manter (0 = manter todos)
            encoding: Encoding do arquivo
        """
        super().__init__(level)
        
        self.filepath_pattern = filepath_pattern
        self.formatter_to_use = formatter
        self.backup_count = backup_count
        self.encoding = encoding
        
        # Estado interno
        self._current_date = None
        self._current_handler: Optional[logging.FileHandler] = None
        self._lock = threading.Lock()
    
    def _get_filepath_for_date(self, date_str: str) -> str:
        """Gera filepath substituindo {date}."""
        return self.filepath_pattern.replace('{date}', date_str)
    
    def _get_current_filepath(self) -> str:
        """Retorna filepath para hoje."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self._get_filepath_for_date(today)
    
    def _should_rollover(self) -> bool:
        """Verifica se precisa criar novo arquivo (mudou o dia)."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self._current_date != today
    
    def _do_rollover(self) -> None:
        """Cria novo arquivo para o dia atual."""
        # Fechar handler antigo
        if self._current_handler:
            self._current_handler.close()
        
        # Atualizar data
        self._current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Criar filepath para hoje
        filepath = self._get_current_filepath()
        
        # Garantir que diretório existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Criar novo handler
        self._current_handler = logging.FileHandler(
            filepath,
            encoding=self.encoding
        )
        
        if self.formatter_to_use:
            self._current_handler.setFormatter(self.formatter_to_use)
        
        # Limpar arquivos antigos
        self._cleanup_old_files()
    
    def _cleanup_old_files(self) -> None:
        """Remove arquivos mais antigos que backup_count."""
        if self.backup_count <= 0:
            return
        
        try:
            # Extrair diretório e padrão de nome
            directory = os.path.dirname(self.filepath_pattern)
            
            # Substituir {date} por padrão glob
            filename_pattern = os.path.basename(self.filepath_pattern)
            glob_pattern = filename_pattern.replace('{date}', '*')
            
            # Buscar todos os arquivos que correspondem ao padrão
            pattern_path = os.path.join(directory, glob_pattern)
            files = glob.glob(pattern_path)
            
            # Ordenar por data de modificação (mais antigo primeiro)
            files.sort(key=lambda x: os.path.getmtime(x))
            
            # Deletar arquivos excedentes
            files_to_delete = len(files) - self.backup_count
            if files_to_delete > 0:
                for filepath in files[:files_to_delete]:
                    try:
                        os.remove(filepath)
                        print(f"🗑️ Log antigo removido: {os.path.basename(filepath)}")
                    except Exception as e:
                        print(f"⚠️ Erro ao remover {filepath}: {e}")
        
        except Exception as e:
            print(f"⚠️ Erro na limpeza de logs antigos: {e}")
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emite log, criando novo arquivo se mudou o dia.
        Thread-safe para múltiplos bots.
        
        Args:
            record: LogRecord a processar
        """
        with self._lock:  # Thread safety
            # Verificar se precisa criar novo arquivo (mudou o dia)
            if self._current_handler is None or self._should_rollover():
                self._do_rollover()
            
            # Emitir no handler atual
            if self._current_handler:
                self._current_handler.emit(record)
    
    def setFormatter(self, fmt: logging.Formatter) -> None:
        """Define formatador."""
        self.formatter_to_use = fmt
        if self._current_handler:
            self._current_handler.setFormatter(fmt)
    
    def close(self) -> None:
        """Fecha handler."""
        if self._current_handler:
            self._current_handler.close()
        super().close()


class CategoryFilterHandler(logging.Handler):
    """
    Handler wrapper que filtra logs por categoria.
    
    Permite rotear logs específicos para handlers especializados.
    """
    
    def __init__(
        self,
        base_handler: logging.Handler,
        categories: Optional[Set[LogCategory]] = None,
        exclude_categories: Optional[Set[LogCategory]] = None
    ):
        """
        Inicializa handler com filtro de categorias.
        
        Args:
            base_handler: Handler real que fará o logging
            categories: Categorias permitidas (None = todas)
            exclude_categories: Categorias excluídas
        """
        super().__init__()
        self.base_handler = base_handler
        self.categories = categories
        self.exclude_categories = exclude_categories or set()
        
        # Copiar nível do handler base
        self.setLevel(base_handler.level)
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emite log apenas se passar pelos filtros de categoria.
        
        Args:
            record: LogRecord a processar
        """
        # Extrair LogEvent se presente
        log_event = getattr(record, 'log_event', None)
        
        if log_event:
            # Verificar filtros de categoria
            if not self._should_log_category(log_event.category):
                return
        
        # Passar para handler base
        self.base_handler.emit(record)
    
    def _should_log_category(self, category: LogCategory) -> bool:
        """
        Verifica se a categoria deve ser logada.
        
        Args:
            category: Categoria a verificar
            
        Returns:
            True se deve logar
        """
        # Se está na lista de exclusão, não logar
        if category in self.exclude_categories:
            return False
        
        # Se não há whitelist, permitir todas (exceto exclusões)
        if self.categories is None:
            return True
        
        # Se há whitelist, só permitir as que estão nela
        return category in self.categories
    
    def setFormatter(self, fmt: logging.Formatter) -> None:
        """Define formatador no handler base."""
        self.base_handler.setFormatter(fmt)
    
    def close(self) -> None:
        """Fecha handler base."""
        self.base_handler.close()
        super().close()


class ConditionalHandler(logging.Handler):
    """
    Handler que só cria arquivo quando recebe primeiro log.
    
    Versão simplificada do LazyFileHandler, mais fácil de manter.
    """
    
    def __init__(
        self,
        filepath: str,
        level: int = logging.DEBUG,
        formatter: Optional[logging.Formatter] = None,
        when: str = 'midnight',
        backup_count: int = 30
    ):
        """
        Inicializa handler condicional.
        
        Args:
            filepath: Caminho do arquivo
            level: Nível do handler
            formatter: Formatador a usar
            when: Quando rodar
            backup_count: Backups a manter
        """
        super().__init__()
        self.filepath = filepath
        self.handler_level = level
        self.formatter_to_use = formatter
        self.when = when
        self.backup_count = backup_count
        self.real_handler: Optional[logging.Handler] = None
        
        self.setLevel(level)
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emite log, criando handler real se necessário.
        
        Args:
            record: LogRecord a processar
        """
        # Criar handler real se ainda não existe
        if self.real_handler is None:
            self._create_real_handler()
        
        # Emitir no handler real
        if self.real_handler:
            self.real_handler.emit(record)
    
    def _create_real_handler(self) -> None:
        """Cria o handler real quando necessário."""
        try:
            self.real_handler = FileHandlerFactory.create_rotating_handler(
                filepath=self.filepath,
                level=self.handler_level,
                formatter=self.formatter_to_use,
                when=self.when,
                backup_count=self.backup_count
            )
        except Exception as e:
            print(f"⚠️ Erro ao criar handler de arquivo: {e}")
    
    def setFormatter(self, fmt: logging.Formatter) -> None:
        """Define formatador."""
        self.formatter_to_use = fmt
        if self.real_handler:
            self.real_handler.setFormatter(fmt)
    
    def close(self) -> None:
        """Fecha handler real se existir."""
        if self.real_handler:
            self.real_handler.close()
        super().close()

