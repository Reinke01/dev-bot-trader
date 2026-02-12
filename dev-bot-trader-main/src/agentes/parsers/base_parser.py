import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class BaseParser(ABC):
    """Parser base para todos os agentes"""
    
    # Regex compilada para performance
    JSON_PATTERN = re.compile(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', re.DOTALL)
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    def extract_json(self, text: str) -> Optional[Dict]:
        """Extração básica de JSON"""
        matches = self.JSON_PATTERN.findall(text)
        
        if not matches:
            return None
            
        for match in reversed(matches):
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return None
    
    @abstractmethod
    def validate(self, data: Dict) -> bool:
        """Validação específica do agente"""
        pass
    
    @abstractmethod
    def parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse completo da resposta"""
        pass
    
    def log_error(self, error: str, data: Any = None):
        """Log de erros padronizado"""
        print(f"[{self.agent_name}] Parser Error: {error}")
        if data:
            print(f"Data: {data}")