"""
Fibonacci Analysis Module
Análise profissional com retracements e extensions
Autor: Sistema de Análise Profissional
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List

class FibonacciAnalyzer:
    """
    Análise Fibonacci completa:
    - Auto-detecção de swing high/low
    - Retracements (23.6%, 38.2%, 50%, 61.8%, 78.6%)
    - Extensions (127.2%, 161.8%, 261.8%)
    - Zonas de confluência
    """
    
    # Níveis de Fibonacci
    RETRACEMENT_LEVELS = {
        '0.0': 0.000,
        '23.6': 0.236,
        '38.2': 0.382,
        '50.0': 0.500,
        '61.8': 0.618,
        '78.6': 0.786,
        '100.0': 1.000
    }
    
    EXTENSION_LEVELS = {
        '0.0': 0.000,
        '61.8': 0.618,
        '100.0': 1.000,
        '127.2': 1.272,
        '161.8': 1.618,
        '200.0': 2.000,
        '261.8': 2.618
    }
    
    @staticmethod
    def find_significant_swing(df: pd.DataFrame, lookback: int = 50) -> Tuple[float, float, int, int]:
        """
        Encontra swing significativo (maior movimento recente)
        
        Returns:
            (swing_high, swing_low, high_index, low_index)
        """
        recent_df = df.tail(lookback)
        
        # Encontrar máxima e mínima do período
        high_idx = recent_df['maxima'].idxmax()
        low_idx = recent_df['minima'].idxmin()
        
        swing_high = recent_df.loc[high_idx, 'maxima']
        swing_low = recent_df.loc[low_idx, 'minima']
        
        # Índices relativos ao DataFrame original
        high_index = df.index.get_loc(high_idx)
        low_index = df.index.get_loc(low_idx)
        
        return swing_high, swing_low, high_index, low_index
    
    @classmethod
    def calculate_retracements(cls, swing_high: float, swing_low: float, direction: str = 'up') -> Dict[str, float]:
        """
        Calcula níveis de retração de Fibonacci
        
        Args:
            swing_high: Topo do movimento
            swing_low: Fundo do movimento
            direction: 'up' (retração de alta) ou 'down' (retração de baixa)
            
        Returns:
            Dict com níveis de preço para cada retração
        """
        diff = swing_high - swing_low
        
        levels = {}
        
        if direction == 'up':
            # Retração de um movimento de alta (preços abaixo do topo)
            for name, ratio in cls.RETRACEMENT_LEVELS.items():
                levels[name] = swing_high - (diff * ratio)
        else:
            # Retração de um movimento de baixa (preços acima do fundo)
            for name, ratio in cls.RETRACEMENT_LEVELS.items():
                levels[name] = swing_low + (diff * ratio)
        
        return levels
    
    @classmethod
    def calculate_extensions(cls, swing_high: float, swing_low: float, direction: str = 'up') -> Dict[str, float]:
        """
        Calcula níveis de extensão de Fibonacci
        
        Args:
            swing_high: Topo do movimento
            swing_low: Fundo do movimento
            direction: 'up' (extensão de alta) ou 'down' (extensão de baixa)
            
        Returns:
            Dict com níveis de preço para cada extensão
        """
        diff = swing_high - swing_low
        
        levels = {}
        
        if direction == 'up':
            # Extensão de um movimento de alta (preços acima do topo)
            for name, ratio in cls.EXTENSION_LEVELS.items():
                levels[name] = swing_low + (diff * ratio)
        else:
            # Extensão de um movimento de baixa (preços abaixo do fundo)
            for name, ratio in cls.EXTENSION_LEVELS.items():
                levels[name] = swing_high - (diff * ratio)
        
        return levels
    
    @staticmethod
    def find_nearest_level(price: float, levels: Dict[str, float], tolerance: float = 0.01) -> Dict[str, any]:
        """
        Encontra o nível de Fibonacci mais próximo do preço atual
        
        Args:
            price: Preço atual
            levels: Dict com níveis de Fibonacci
            tolerance: Tolerância em % para considerar "tocando" o nível
            
        Returns:
            Dict com informações sobre o nível mais próximo
        """
        nearest_level = None
        min_distance = float('inf')
        
        for level_name, level_price in levels.items():
            distance = abs(price - level_price)
            distance_pct = (distance / price) * 100
            
            if distance < min_distance:
                min_distance = distance
                nearest_level = {
                    'name': level_name,
                    'price': level_price,
                    'distance': distance,
                    'distance_pct': distance_pct,
                    'touching': distance_pct < tolerance
                }
        
        return nearest_level
    
    @staticmethod
    def identify_support_resistance(price: float, retracements: Dict[str, float], extensions: Dict[str, float]) -> List[Dict[str, any]]:
        """
        Identifica suportes e resistências com base em Fibonacci
        
        Returns:
            Lista de níveis significativos ordenados por proximidade
        """
        levels = []
        
        # Combinar todos os níveis
        all_levels = {**retracements, **extensions}
        
        for name, level_price in all_levels.items():
            distance_pct = abs((price - level_price) / price) * 100
            
            if distance_pct < 5:  # Apenas níveis próximos (< 5%)
                levels.append({
                    'name': name,
                    'price': level_price,
                    'distance_pct': distance_pct,
                    'type': 'Suporte' if level_price < price else 'Resistência'
                })
        
        # Ordenar por proximidade
        levels.sort(key=lambda x: x['distance_pct'])
        
        return levels
    
    @classmethod
    def analyze_fibonacci(cls, df: pd.DataFrame) -> Dict[str, any]:
        """
        Análise completa de Fibonacci
        
        Returns:
            Dict com análise completa e score 0-100
        """
        # Encontrar swing significativo
        swing_high, swing_low, high_idx, low_idx = cls.find_significant_swing(df)
        
        # Determinar direção do movimento
        # Se o topo veio depois do fundo = movimento de alta
        # Se o fundo veio depois do topo = movimento de baixa
        if high_idx > low_idx:
            direction = 'up'
            last_move = 'ALTA'
        else:
            direction = 'down'
            last_move = 'BAIXA'
        
        # Calcular níveis
        retracements = cls.calculate_retracements(swing_high, swing_low, direction)
        extensions = cls.calculate_extensions(swing_high, swing_low, direction)
        
        # Preço atual
        preco_atual = df['fechamento'].iloc[-1]
        
        # Encontrar nível mais próximo
        nearest_retracement = cls.find_nearest_level(preco_atual, retracements)
        nearest_extension = cls.find_nearest_level(preco_atual, extensions)
        
        # Identificar suportes e resistências
        sr_levels = cls.identify_support_resistance(preco_atual, retracements, extensions)
        
        # Calcular score baseado em proximidade de níveis chave
        score = 0
        
        # Níveis chave: 38.2%, 50%, 61.8% (mais importantes)
        key_levels = ['38.2', '50.0', '61.8']
        
        for level_name in key_levels:
            if level_name in retracements:
                level_price = retracements[level_name]
                distance_pct = abs((preco_atual - level_price) / preco_atual) * 100
                
                # Quanto mais próximo, maior o score
                if distance_pct < 0.5:
                    score += 30  # Muito próximo
                elif distance_pct < 1.0:
                    score += 20
                elif distance_pct < 2.0:
                    score += 10
        
        # Bônus se tocando golden ratio (61.8%)
        if nearest_retracement and nearest_retracement['name'] == '61.8' and nearest_retracement['touching']:
            score += 20
        
        # Limitar score a 100
        score = min(score, 100)
        
        return {
            'swing_high': swing_high,
            'swing_low': swing_low,
            'last_move': last_move,
            'price_current': preco_atual,
            'retracements': retracements,
            'extensions': extensions,
            'nearest_retracement': nearest_retracement,
            'nearest_extension': nearest_extension,
            'support_resistance_levels': sr_levels,
            'score': score,
            'interpretation': cls._interpret_fibonacci(preco_atual, retracements, nearest_retracement)
        }
    
    @staticmethod
    def _interpret_fibonacci(price: float, retracements: Dict[str, float], nearest: Dict[str, any]) -> str:
        """
        Interpreta a posição do preço em relação aos níveis de Fibonacci
        """
        if not nearest:
            return "Sem níveis próximos"
        
        level_name = nearest['name']
        touching = nearest['touching']
        
        interpretations = {
            '23.6': "Retração fraca - Tendência forte",
            '38.2': "Retração ideal - Zona de compra/venda comum",
            '50.0': "Retração média - Zona psicológica importante",
            '61.8': "Golden Ratio - Zona crítica de decisão",
            '78.6': "Retração profunda - Possível reversão"
        }
        
        base_interp = interpretations.get(level_name, "Nível de Fibonacci")
        
        if touching:
            return f"🎯 TOCANDO {level_name}% - {base_interp}"
        else:
            dist = nearest['distance_pct']
            return f"Próximo de {level_name}% ({dist:.1f}%) - {base_interp}"
