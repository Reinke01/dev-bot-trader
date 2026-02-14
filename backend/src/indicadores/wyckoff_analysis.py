"""
Wyckoff Analysis Module
Análise profissional usando método Wyckoff e VSA (Volume Spread Analysis)
Autor: Sistema de Análise Profissional
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class WyckoffAnalyzer:
    """
    Implementa o método Wyckoff completo:
    - Fases: Acumulação, Markup, Distribuição, Markdown
    - VSA: Volume Spread Analysis
    - Spring Detection (mola)
    - Upthrust Detection (empurrão para cima)
    - Sign of Strength/Weakness (SOS/SOW)
    """
    
    # Fases do Wyckoff
    PHASES = {
        'ACCUMULATION': 'Acumulação - Smart Money comprando',
        'MARKUP': 'Markup - Tendência de Alta',
        'DISTRIBUTION': 'Distribuição - Smart Money vendendo',
        'MARKDOWN': 'Markdown - Tendência de Baixa'
    }
    
    @staticmethod
    def calculate_volume_profile(df: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        """
        Calcula perfil de volume
        
        Returns:
            Dict com métricas de volume
        """
        volume_ma = df['volume'].rolling(window=period).mean()
        volume_std = df['volume'].rolling(window=period).std()
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = volume_ma.iloc[-1]
        
        volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1
        volume_zscore = (current_volume - avg_volume) / volume_std.iloc[-1] if volume_std.iloc[-1] > 0 else 0
        
        return {
            'current': current_volume,
            'average': avg_volume,
            'ratio': volume_ratio,
            'zscore': volume_zscore,
            'is_climax': volume_ratio > 2.0  # Climax se 2x acima da média
        }
    
    @staticmethod
    def calculate_spread(df: pd.DataFrame) -> float:
        """
        Calcula o spread da vela (range)
        """
        return df['maxima'].iloc[-1] - df['minima'].iloc[-1]
    
    @staticmethod
    def detect_spring(df: pd.DataFrame, lookback: int = 20) -> Dict[str, any]:
        """
        Detecta Spring (Mola)
        Spring = Falsa quebra de suporte seguida de reversão forte
        
        Características:
        - Preço quebra suporte recente
        - Volume relativamente baixo na quebra
        - Reversão rápida com volume aumentando
        
        Returns:
            Dict com informações sobre spring detected
        """
        recent_df = df.tail(lookback)
        
        # Encontrar mínima recente
        support_level = recent_df['minima'].min()
        support_idx = recent_df['minima'].idxmin()
        
        # Verificar últimas 5 velas
        last_5 = df.tail(5)
        
        spring_detected = False
        spring_strength = 0
        
        for i in range(len(last_5) - 1):
            current_low = last_5['minima'].iloc[i]
            current_close = last_5['fechamento'].iloc[i]
            current_volume = last_5['volume'].iloc[i]
            
            next_close = last_5['fechamento'].iloc[i + 1]
            next_volume = last_5['volume'].iloc[i + 1]
            
            # Quebrou suporte?
            if current_low < support_level:
                # Volume na quebra é baixo?
                avg_volume = recent_df['volume'].mean()
                
                if current_volume < avg_volume:
                    # Reversão forte no próximo candle?
                    if next_close > current_close and next_volume > current_volume * 1.5:
                        spring_detected = True
                        spring_strength = ((next_close - current_low) / current_low) * 100
                        break
        
        return {
            'detected': spring_detected,
            'strength': spring_strength,
            'signal': 'COMPRA FORTE' if spring_detected else None
        }
    
    @staticmethod
    def detect_upthrust(df: pd.DataFrame, lookback: int = 20) -> Dict[str, any]:
        """
        Detecta Upthrust (Empurrão para cima)
        Upthrust = Falsa quebra de resistência seguida de queda
        
        Características:
        - Preço quebra resistência recente
        - Volume alto na quebra (climax)
        - Reversão rápida para baixo
        
        Returns:
            Dict com informações sobre upthrust detected
        """
        recent_df = df.tail(lookback)
        
        # Encontrar máxima recente
        resistance_level = recent_df['maxima'].max()
        
        # Verificar últimas 5 velas
        last_5 = df.tail(5)
        
        upthrust_detected = False
        upthrust_strength = 0
        
        for i in range(len(last_5) - 1):
            current_high = last_5['maxima'].iloc[i]
            current_close = last_5['fechamento'].iloc[i]
            current_volume = last_5['volume'].iloc[i]
            
            next_close = last_5['fechamento'].iloc[i + 1]
            next_volume = last_5['volume'].iloc[i + 1]
            
            # Quebrou resistência?
            if current_high > resistance_level:
                # Volume alto na quebra?
                avg_volume = recent_df['volume'].mean()
                
                if current_volume > avg_volume * 1.5:
                    # Reversão para baixo?
                    if next_close < current_close:
                        upthrust_detected = True
                        upthrust_strength = ((current_high - next_close) / current_high) * 100
                        break
        
        return {
            'detected': upthrust_detected,
            'strength': upthrust_strength,
            'signal': 'VENDA FORTE' if upthrust_detected else None
        }
    
    @staticmethod
    def detect_sign_of_strength(df: pd.DataFrame) -> Dict[str, any]:
        """
        Detecta Sign of Strength (SOS)
        SOS = Vela forte de alta com volume acima da média
        
        Returns:
            Dict com informações sobre SOS
        """
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Calcular body da vela
        body = last_candle['fechamento'] - last_candle['abertura']
        body_pct = (body / last_candle['abertura']) * 100
        
        # Calcular range
        candle_range = last_candle['maxima'] - last_candle['minima']
        body_to_range = (body / candle_range) if candle_range > 0 else 0
        
        # Volume
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = last_candle['volume'] / avg_volume if avg_volume > 0 else 1
        
        # SOS se:
        # 1. Vela de alta forte (body > 1%)
        # 2. Body ocupa maior parte do range (> 60%)
        # 3. Volume acima da média (> 1.2x)
        # 4. Fecha próximo da máxima
        
        close_near_high = (last_candle['maxima'] - last_candle['fechamento']) / candle_range < 0.2 if candle_range > 0 else False
        
        is_sos = (
            body_pct > 1.0 and
            body_to_range > 0.6 and
            volume_ratio > 1.2 and
            close_near_high
        )
        
        strength = (body_pct * 0.4 + body_to_range * 30 + (volume_ratio - 1) * 30)
        
        return {
            'detected': is_sos,
            'strength': strength,
            'body_pct': body_pct,
            'volume_ratio': volume_ratio
        }
    
    @staticmethod
    def detect_sign_of_weakness(df: pd.DataFrame) -> Dict[str, any]:
        """
        Detecta Sign of Weakness (SOW)
        SOW = Vela forte de baixa com volume acima da média
        
        Returns:
            Dict com informações sobre SOW
        """
        last_candle = df.iloc[-1]
        
        # Calcular body da vela
        body = last_candle['abertura'] - last_candle['fechamento']
        body_pct = (body / last_candle['abertura']) * 100
        
        # Calcular range
        candle_range = last_candle['maxima'] - last_candle['minima']
        body_to_range = (body / candle_range) if candle_range > 0 else 0
        
        # Volume
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = last_candle['volume'] / avg_volume if avg_volume > 0 else 1
        
        # SOW se:
        # 1. Vela de baixa forte (body > 1%)
        # 2. Body ocupa maior parte do range (> 60%)
        # 3. Volume acima da média (> 1.2x)
        # 4. Fecha próximo da mínima
        
        close_near_low = (last_candle['fechamento'] - last_candle['minima']) / candle_range < 0.2 if candle_range > 0 else False
        
        is_sow = (
            body_pct > 1.0 and
            body_to_range > 0.6 and
            volume_ratio > 1.2 and
            close_near_low
        )
        
        strength = (body_pct * 0.4 + body_to_range * 30 + (volume_ratio - 1) * 30)
        
        return {
            'detected': is_sow,
            'strength': strength,
            'body_pct': body_pct,
            'volume_ratio': volume_ratio
        }
    
    @classmethod
    def identify_phase(cls, df: pd.DataFrame, lookback: int = 50) -> str:
        """
        Identifica a fase atual do Wyckoff
        
        Returns:
            'ACCUMULATION', 'MARKUP', 'DISTRIBUTION', 'MARKDOWN'
        """
        recent_df = df.tail(lookback)
        
        # Analisar volatilidade (range médio)
        avg_range = (recent_df['maxima'] - recent_df['minima']).mean()
        current_range = df['maxima'].iloc[-1] - df['minima'].iloc[-1]
        
        # Analisar volume médio
        avg_volume = recent_df['volume'].mean()
        recent_avg_volume = df['volume'].tail(10).mean()
        
        # Analisar tendência de preço
        price_trend = df['fechamento'].iloc[-1] - df['fechamento'].iloc[-lookback]
        price_trend_pct = (price_trend / df['fechamento'].iloc[-lookback]) * 100
        
        # Lógica de identificação
        # Acumulação: Baixa volatilidade, volume médio/alto, preço lateral
        if abs(price_trend_pct) < 5 and current_range < avg_range and recent_avg_volume >= avg_volume:
            return 'ACCUMULATION'
        
        # Markup: Alta, volume crescente, range crescente
        elif price_trend_pct > 5 and recent_avg_volume > avg_volume:
            return 'MARKUP'
        
        # Distribuição: Baixa volatilidade, volume alto, preço lateral após alta
        elif abs(price_trend_pct) < 5 and current_range < avg_range and recent_avg_volume > avg_volume * 1.5:
            return 'DISTRIBUTION'
        
        # Markdown: Baixa, volume crescente
        elif price_trend_pct < -5:
            return 'MARKDOWN'
        
        return 'ACCUMULATION'  # Default
    
    @classmethod
    def analyze_wyckoff(cls, df: pd.DataFrame) -> Dict[str, any]:
        """
        Análise completa Wyckoff
        
        Returns:
            Dict com análise completa e score 0-100
        """
        # Identificar fase
        phase = cls.identify_phase(df)
        phase_description = cls.PHASES.get(phase, 'Desconhecido')
        
        # Volume profile
        volume_profile = cls.calculate_volume_profile(df)
        
        # Detectar padrões
        spring = cls.detect_spring(df)
        upthrust = cls.detect_upthrust(df)
        sos = cls.detect_sign_of_strength(df)
        sow = cls.detect_sign_of_weakness(df)
        
        # Calcular score
        score = 0
        signals = []
        
        # Fase favorável
        if phase == 'ACCUMULATION':
            score += 30
            signals.append('Fase de Acumulação - Oportunidade de Compra')
        elif phase == 'MARKUP':
            score += 20
            signals.append('Fase de Markup - Tendência de Alta')
        elif phase == 'DISTRIBUTION':
            score -= 20
            signals.append('Fase de Distribuição - Cuidado')
        elif phase == 'MARKDOWN':
            score -= 10
            signals.append('Fase de Markdown - Tendência de Baixa')
        
        # Spring (muito bullish)
        if spring['detected']:
            score += 40
            signals.append(f"🚀 SPRING DETECTADO - {spring['signal']}")
        
        # Upthrust (muito bearish)
        if upthrust['detected']:
            score -= 30
            signals.append(f"⚠️ UPTHRUST DETECTADO - {upthrust['signal']}")
        
        # SOS (bullish)
        if sos['detected']:
            score += 20
            signals.append('Sign of Strength - Força Compradora')
        
        # SOW (bearish)
        if sow['detected']:
            score -= 20
            signals.append('Sign of Weakness - Força Vendedora')
        
        # Volume climax
        if volume_profile['is_climax']:
            score += 10
            signals.append('Volume Climax - Possível Reversão')
        
        # Normalizar score para 0-100
        score = max(0, min(score, 100))
        
        return {
            'phase': phase,
            'phase_description': phase_description,
            'volume_profile': volume_profile,
            'spring': spring,
            'upthrust': upthrust,
            'sign_of_strength': sos,
            'sign_of_weakness': sow,
            'score': score,
            'signals': signals
        }
