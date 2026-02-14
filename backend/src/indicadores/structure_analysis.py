"""
Structure Analysis Module
Análise profissional de estrutura de mercado
Autor: Sistema de Análise Profissional
"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from scipy.signal import find_peaks

class StructureAnalyzer:
    """
    Analisa a estrutura do mercado identificando:
    - Higher Highs (HH) / Higher Lows (HL) = Tendência de Alta
    - Lower Highs (LH) / Lower Lows (LL) = Tendência de Baixa
    - Break of Structure (BOS) = Quebra de estrutura
    - Change of Character (ChoCH) = Mudança de caráter
    """
    
    @staticmethod
    def find_swing_points(df: pd.DataFrame, left_bars: int = 5, right_bars: int = 5) -> Tuple[List[int], List[int]]:
        """
        Identifica swing highs e swing lows
        
        Args:
            df: DataFrame com dados OHLCV
            left_bars: Barras à esquerda para validação
            right_bars: Barras à direita para validação
            
        Returns:
            (swing_highs_indices, swing_lows_indices)
        """
        # Encontrar topos (swing highs)
        highs = df['maxima'].values
        swing_highs, _ = find_peaks(highs, distance=left_bars+right_bars)
        
        # Encontrar fundos (swing lows)
        lows = df['minima'].values
        swing_lows, _ = find_peaks(-lows, distance=left_bars+right_bars)
        
        return swing_highs.tolist(), swing_lows.tolist()
    
    @staticmethod
    def classify_structure(swing_highs: List[Tuple[int, float]], swing_lows: List[Tuple[int, float]]) -> str:
        """
        Classifica a estrutura do mercado
        
        Args:
            swing_highs: Lista de (índice, valor) dos topos
            swing_lows: Lista de (índice, valor) dos fundos
            
        Returns:
            'HH_HL': Higher Highs + Higher Lows (Alta)
            'LH_LL': Lower Highs + Lower Lows (Baixa)
            'HH_LL': Higher Highs + Lower Lows (Expansão)
            'LH_HL': Lower Highs + Higher Lows (Compressão/Lateral)
        """
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return "INDEFINIDO"
        
        # Analisar últimos 3 topos
        recent_highs = swing_highs[-3:] if len(swing_highs) >= 3 else swing_highs
        higher_highs = all(recent_highs[i][1] > recent_highs[i-1][1] for i in range(1, len(recent_highs)))
        lower_highs = all(recent_highs[i][1] < recent_highs[i-1][1] for i in range(1, len(recent_highs)))
        
        # Analisar últimos 3 fundos
        recent_lows = swing_lows[-3:] if len(swing_lows) >= 3 else swing_lows
        higher_lows = all(recent_lows[i][1] > recent_lows[i-1][1] for i in range(1, len(recent_lows)))
        lower_lows = all(recent_lows[i][1] < recent_lows[i-1][1] for i in range(1, len(recent_lows)))
        
        # Classificação
        if higher_highs and higher_lows:
            return "HH_HL"  # Tendência de Alta clara
        elif lower_highs and lower_lows:
            return "LH_LL"  # Tendência de Baixa clara
        elif higher_highs and lower_lows:
            return "HH_LL"  # Expansão (volatilidade aumentando)
        elif lower_highs and higher_lows:
            return "LH_HL"  # Compressão (lateralização)
        else:
            return "MISTO"  # Estrutura indefinida
    
    @staticmethod
    def detect_bos(df: pd.DataFrame, swing_highs: List[int], swing_lows: List[int]) -> Dict[str, any]:
        """
        Detecta Break of Structure (BOS)
        BOS = Quando o preço quebra um topo/fundo significativo
        
        Returns:
            Dict com informações sobre BOS
        """
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return {'detected': False}
        
        preco_atual = df['fechamento'].iloc[-1]
        
        # Último topo e fundo significativos
        last_high_idx = swing_highs[-1]
        last_low_idx = swing_lows[-1]
        last_high_value = df['maxima'].iloc[last_high_idx]
        last_low_value = df['minima'].iloc[last_low_idx]
        
        # BOS de Alta: Preço quebrou último topo
        if preco_atual > last_high_value:
            return {
                'detected': True,
                'type': 'ALTA',
                'level': last_high_value,
                'strength': ((preco_atual - last_high_value) / last_high_value) * 100
            }
        
        # BOS de Baixa: Preço quebrou último fundo
        elif preco_atual < last_low_value:
            return {
                'detected': True,
                'type': 'BAIXA',
                'level': last_low_value,
                'strength': ((last_low_value - preco_atual) / last_low_value) * 100
            }
        
        return {'detected': False}
    
    @staticmethod
    def detect_choch(df: pd.DataFrame, swing_highs: List[int], swing_lows: List[int]) -> Dict[str, any]:
        """
        Detecta Change of Character (ChoCH)
        ChoCH = Mudança na estrutura que indica possível reversão
        
        Ex: Em tendência de alta (HH_HL), faz um LH = ChoCH
        
        Returns:
            Dict com informações sobre ChoCH
        """
        if len(swing_highs) < 3 or len(swing_lows) < 3:
            return {'detected': False}
        
        # Analisar últimos 3 topos
        last_3_highs = [(i, df['maxima'].iloc[i]) for i in swing_highs[-3:]]
        
        # Analisar últimos 3 fundos
        last_3_lows = [(i, df['minima'].iloc[i]) for i in swing_lows[-3:]]
        
        # Verificar mudança de estrutura nos topos
        if last_3_highs[-1][1] < last_3_highs[-2][1]:  # LH após HHs
            # Verificar se havia HHs antes
            if last_3_highs[-2][1] > last_3_highs[-3][1]:
                return {
                    'detected': True,
                    'type': 'BAIXISTA',
                    'description': 'Lower High após Higher Highs',
                    'signal': 'Possível reversão de alta para baixa'
                }
        
        # Verificar mudança de estrutura nos fundos
        if last_3_lows[-1][1] > last_3_lows[-2][1]:  # HL após LLs
            # Verificar se havia LLs antes
            if last_3_lows[-2][1] < last_3_lows[-3][1]:
                return {
                    'detected': True,
                    'type': 'ALTISTA',
                    'description': 'Higher Low após Lower Lows',
                    'signal': 'Possível reversão de baixa para alta'
                }
        
        return {'detected': False}
    
    @staticmethod
    def calculate_structure_strength(structure_type: str) -> int:
        """
        Calcula força da estrutura (0-100)
        """
        strength_map = {
            'HH_HL': 90,  # Tendência de alta muito forte
            'LH_LL': 90,  # Tendência de baixa muito forte
            'HH_LL': 50,  # Expansão (incerto)
            'LH_HL': 30,  # Compressão/Lateral (fraco)
            'MISTO': 20,  # Indefinido
            'INDEFINIDO': 0
        }
        return strength_map.get(structure_type, 0)
    
    @classmethod
    def analyze_structure(cls, df: pd.DataFrame) -> Dict[str, any]:
        """
        Análise completa de estrutura de mercado
        
        Returns:
            Dict com análise completa e score 0-100
        """
        # Encontrar swing points
        swing_high_indices, swing_low_indices = cls.find_swing_points(df)
        
        if len(swing_high_indices) < 2 or len(swing_low_indices) < 2:
            return {
                'structure_type': 'INDEFINIDO',
                'interpretation': 'Dados insuficientes',
                'score': 0,
                'bos': {'detected': False},
                'choch': {'detected': False}
            }
        
        # Preparar dados de swing points com valores
        swing_highs = [(i, df['maxima'].iloc[i]) for i in swing_high_indices]
        swing_lows = [(i, df['minima'].iloc[i]) for i in swing_low_indices]
        
        # Classificar estrutura
        structure_type = cls.classify_structure(swing_highs, swing_lows)
        
        # Interpretação
        interpretations = {
            'HH_HL': 'Tendência de Alta - Higher Highs + Higher Lows',
            'LH_LL': 'Tendência de Baixa - Lower Highs + Lower Lows',
            'HH_LL': 'Expansão - Volatilidade Aumentando',
            'LH_HL': 'Compressão/Lateral - Consolidação',
            'MISTO': 'Estrutura Mista - Indefinido',
            'INDEFINIDO': 'Dados Insuficientes'
        }
        
        interpretation = interpretations.get(structure_type, 'Desconhecido')
        
        # Detectar BOS e ChoCH
        bos = cls.detect_bos(df, swing_high_indices, swing_low_indices)
        choch = cls.detect_choch(df, swing_high_indices, swing_low_indices)
        
        # Calcular score
        structure_strength = cls.calculate_structure_strength(structure_type)
        
        # Bônus para BOS e ChoCH
        bonus = 0
        if bos['detected']:
            bonus += 10
        if choch['detected']:
            bonus += 10
        
        final_score = min(structure_strength + bonus, 100)
        
        return {
            'structure_type': structure_type,
            'interpretation': interpretation,
            'score': final_score,
            'swing_highs_count': len(swing_highs),
            'swing_lows_count': len(swing_lows),
            'last_swing_high': swing_highs[-1][1] if swing_highs else None,
            'last_swing_low': swing_lows[-1][1] if swing_lows else None,
            'bos': bos,
            'choch': choch
        }
