from typing import Dict, Optional
from .base_parser import BaseParser

class TradeConductorParser(BaseParser):
    """Parser específico para o Trade Conductor"""
    
    def __init__(self):
        super().__init__("TradeConductor")
        
        # Ações válidas específicas
        self.valid_actions = {
            'manter', 'fechar_compra', 'fechar_venda', 
            'ajustar_stop', 'ajustar_alvo', 
            'acionar_trailing_stop_imediato', 'acionar_trailing_stop_preco',
            'realizar_parcial'
        }
    
    def validate(self, data: Dict) -> bool:
        """Validação específica do Trade Conductor"""
        # Campos obrigatórios
        required_fields = {'acoes', 'confianca', 'justificativa'}
        if not required_fields.issubset(data.keys()):
            return False
        
        # Validação da confiança
        confianca = data.get('confianca')
        if not isinstance(confianca, (int, float)) or not (0.0 <= confianca <= 1.0):
            return False
        
        # Validação das ações
        acoes = data.get('acoes', [])
        if not isinstance(acoes, list) or not acoes:
            return False
        
        for acao in acoes:
            if not isinstance(acao, dict):
                return False
            
            acao_tipo = acao.get('acao')
            if acao_tipo not in self.valid_actions:
                return False
            
            # Validações específicas por tipo de ação
            if not self._validate_action(acao):
                return False
        
        return True
    
    def _validate_action(self, acao: Dict) -> bool:
        """Valida ação específica"""
        acao_tipo = acao.get('acao')
        
        # Ações que precisam de preço de stop
        if acao_tipo == 'ajustar_stop':
            return 'preco_stop' in acao and isinstance(acao['preco_stop'], (int, float))
        
        # Ações que precisam de preço alvo
        if acao_tipo == 'ajustar_alvo':
            return 'preco_alvo' in acao and isinstance(acao['preco_alvo'], (int, float))
        
        # Trailing stop imediato
        if acao_tipo == 'acionar_trailing_stop_imediato':
            return 'preco_trailing' in acao and isinstance(acao['preco_trailing'], (int, float))
        
        # Trailing stop com preço
        if acao_tipo == 'acionar_trailing_stop_preco':
            return (
                'preco_trailing' in acao and 
                'preco_acionamento' in acao and
                isinstance(acao['preco_trailing'], (int, float)) and
                isinstance(acao['preco_acionamento'], (int, float))
            )
        
        # Realizar parcial
        if acao_tipo == 'realizar_parcial':
            return 'percentual' in acao and isinstance(acao['percentual'], (int, float))
        
        # Ações simples (manter, fechar_compra, fechar_venda)
        return True
    
    def parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse completo da resposta do Trade Conductor"""
        data = self.extract_json(response_text)
        
        if not data:
            self.log_error("Nenhum JSON encontrado na resposta")
            return None
        
        if not self.validate(data):
            self.log_error("Dados inválidos", data)
            return None
        
        # Normalização específica
        return self._normalize_data(data)
    
    def _normalize_data(self, data: Dict) -> Dict:
        """Normaliza dados específicos do Trade Conductor"""
        # Garante que confiança seja float
        data['confianca'] = float(data['confianca'])
        
        # Normaliza preços nas ações
        for acao in data['acoes']:
            for price_field in ['preco_stop', 'preco_alvo', 'preco_trailing', 'preco_acionamento']:
                if price_field in acao:
                    acao[price_field] = float(acao[price_field])
        
        return data