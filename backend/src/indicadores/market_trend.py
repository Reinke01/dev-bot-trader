"""
Market Trend Analysis Module
Indicadores profissionais para identificar tendência de mercado
Autor: Sistema de Análise Profissional
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict
import pandas_ta as ta

class MarketTrendAnalyzer:
    """
    Analisa a tendência de mercado usando múltiplos indicadores
    - ADX: Força da tendência
    - Supertrend: Direção da tendência
    - Ichimoku: Tendência multi-timeframe
    - Parabolic SAR: Pontos de reversão
    """
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> Tuple[float, str]:
        """
        ADX - Average Directional Index
        Mede a FORÇA da tendência (não a direção)
        
        Returns:
            (adx_value, interpretation)
            ADX < 25: Tendência fraca ou lateral
            ADX 25-50: Tendência moderada
            ADX > 50: Tendência forte
        """
        adx_result = ta.adx(df['maxima'], df['minima'], df['fechamento'], length=period)
        
        if adx_result is None or adx_result.empty:
            return 0.0, "Não disponível"
        
        adx_value = adx_result[f'ADX_{period}'].iloc[-1]
        di_plus = adx_result[f'DMP_{period}'].iloc[-1]
        di_minus = adx_result[f'DMN_{period}'].iloc[-1]
        
        # Interpretação
        if adx_value < 25:
            strength = "Fraca/Lateral"
        elif adx_value < 50:
            strength = "Moderada"
        else:
            strength = "Forte"
        
        direction = "Alta" if di_plus > di_minus else "Baixa"
        
        return adx_value, f"{strength} - {direction}"
    
    @staticmethod
    def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Tuple[str, float, float]:
        """
        Supertrend - Indicador de tendência visual
        
        Returns:
            (trend, supertrend_value, signal_strength)
            trend: 'ALTA' ou 'BAIXA'
            signal_strength: 0-10 (baseado em distância)
        """
        supertrend_result = ta.supertrend(
            df['maxima'], 
            df['minima'], 
            df['fechamento'], 
            length=period, 
            multiplier=multiplier
        )
        
        if supertrend_result is None or supertrend_result.empty:
            return "Indefinido", 0.0, 0.0
        
        st_value = supertrend_result[f'SUPERT_{period}_{multiplier}'].iloc[-1]
        st_direction = supertrend_result[f'SUPERTd_{period}_{multiplier}'].iloc[-1]
        preco_atual = df['fechamento'].iloc[-1]
        
        trend = "ALTA" if st_direction == 1 else "BAIXA"
        
        # Força do sinal baseada na distância do preço ao Supertrend
        distancia_pct = abs((preco_atual - st_value) / st_value) * 100
        signal_strength = min(distancia_pct * 2, 10)  # 0-10 scale
        
        return trend, st_value, signal_strength
    
    @staticmethod
    def calculate_ichimoku(df: pd.DataFrame) -> Dict[str, any]:
        """
        Ichimoku Cloud - Sistema completo de tendência
        
        Returns:
            Dict com todos os componentes e interpretação
        """
        ichimoku = ta.ichimoku(df['maxima'], df['minima'], df['fechamento'])
        
        if ichimoku is None or len(ichimoku) == 0:
            return {
                'trend': 'Indefinido',
                'cloud_color': 'Neutro',
                'position': 'Dentro',
                'score': 0
            }
        
        # Componentes do Ichimoku
        tenkan = ichimoku[0]['ITS_9'].iloc[-1]  # Conversão
        kijun = ichimoku[0]['IKS_26'].iloc[-1]  # Base
        senkou_a = ichimoku[0]['ISA_9'].iloc[-26] if len(ichimoku[0]) > 26 else ichimoku[0]['ISA_9'].iloc[-1]  # Leading Span A
        senkou_b = ichimoku[0]['ISB_26'].iloc[-26] if len(ichimoku[0]) > 26 else ichimoku[0]['ISB_26'].iloc[-1]  # Leading Span B
        
        preco_atual = df['fechamento'].iloc[-1]
        
        # Análise
        cloud_color = "Alta" if senkou_a > senkou_b else "Baixa"
        
        # Posição do preço em relação à nuvem
        if preco_atual > max(senkou_a, senkou_b):
            position = "Acima da Nuvem"
            position_score = 3
        elif preco_atual < min(senkou_a, senkou_b):
            position = "Abaixo da Nuvem"
            position_score = -3
        else:
            position = "Dentro da Nuvem"
            position_score = 0
        
        # Cruzamento TK
        tk_signal = 0
        if tenkan > kijun:
            tk_signal = 2
        elif tenkan < kijun:
            tk_signal = -2
        
        # Score total
        score = position_score + tk_signal
        
        return {
            'trend': cloud_color,
            'cloud_color': cloud_color,
            'position': position,
            'tk_cross': "Alta" if tenkan > kijun else "Baixa",
            'score': score,
            'tenkan': tenkan,
            'kijun': kijun
        }
    
    @staticmethod
    def calculate_parabolic_sar(df: pd.DataFrame) -> Tuple[str, float, bool]:
        """
        Parabolic SAR - Stop and Reverse
        Identifica pontos de reversão de tendência
        
        Returns:
            (trend, sar_value, is_reversal)
        """
        sar = ta.psar(df['maxima'], df['minima'], df['fechamento'])
        
        if sar is None or sar.empty:
            return "Indefinido", 0.0, False
        
        sar_long = sar['PSARl_0.02_0.2'].iloc[-1]
        sar_short = sar['PSARs_0.02_0.2'].iloc[-1]
        preco_atual = df['fechamento'].iloc[-1]
        
        # Detectar reversão
        sar_long_prev = sar['PSARl_0.02_0.2'].iloc[-2]
        sar_short_prev = sar['PSARs_0.02_0.2'].iloc[-2]
        
        is_reversal = False
        if pd.notna(sar_long) and pd.isna(sar_long_prev):
            is_reversal = True  # Reversão para alta
        elif pd.notna(sar_short) and pd.isna(sar_short_prev):
            is_reversal = True  # Reversão para baixa
        
        # Tendência atual
        if pd.notna(sar_long):
            trend = "ALTA"
            sar_value = sar_long
        else:
            trend = "BAIXA"
            sar_value = sar_short
        
        return trend, sar_value, is_reversal
    
    @classmethod
    def analyze_trend(cls, df: pd.DataFrame) -> Dict[str, any]:
        """
        Análise completa de tendência
        Combina todos os indicadores para decisão final
        
        Returns:
            Dict com análise completa e score de 0-100
        """
        # Calcular todos os indicadores
        adx_value, adx_interp = cls.calculate_adx(df)
        st_trend, st_value, st_strength = cls.calculate_supertrend(df)
        ichimoku_data = cls.calculate_ichimoku(df)
        sar_trend, sar_value, sar_reversal = cls.calculate_parabolic_sar(df)
        
        # Sistema de votação para tendência
        votes_alta = 0
        votes_baixa = 0
        
        if st_trend == "ALTA":
            votes_alta += 1
        else:
            votes_baixa += 1
        
        if ichimoku_data['cloud_color'] == "Alta":
            votes_alta += 1
        else:
            votes_baixa += 1
        
        if sar_trend == "ALTA":
            votes_alta += 1
        else:
            votes_baixa += 1
        
        # Tendência final
        if votes_alta > votes_baixa:
            trend_final = "ALTA"
            trend_confidence = (votes_alta / 3) * 100
        elif votes_baixa > votes_alta:
            trend_final = "BAIXA"
            trend_confidence = (votes_baixa / 3) * 100
        else:
            trend_final = "LATERAL"
            trend_confidence = 50
        
        # Score de qualidade da tendência (0-100)
        trend_quality = adx_value  # ADX já está em escala 0-100
        
        # Score final (média ponderada)
        final_score = (trend_quality * 0.6 + trend_confidence * 0.4)
        
        return {
            'trend': trend_final,
            'confidence': trend_confidence,
            'quality': trend_quality,
            'score': final_score,
            'adx': {
                'value': adx_value,
                'interpretation': adx_interp
            },
            'supertrend': {
                'trend': st_trend,
                'value': st_value,
                'strength': st_strength
            },
            'ichimoku': ichimoku_data,
            'parabolic_sar': {
                'trend': sar_trend,
                'value': sar_value,
                'reversal_detected': sar_reversal
            }
        }
