"""
Advanced Scoring System
Sistema profissional de pontuação 0-100
Combina todos os indicadores com pesos otimizados
Autor: Sistema de Análise Profissional
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from corretoras.funcoes_bybit import busca_velas
from managers.data_manager import prepare_market_data
from indicadores.market_trend import MarketTrendAnalyzer
from indicadores.structure_analysis import StructureAnalyzer
from indicadores.fibonacci_analysis import FibonacciAnalyzer
from indicadores.wyckoff_analysis import WyckoffAnalyzer
from indicadores.bandas_bollinger import bandas_bollinger
from indicadores.indicadores_osciladores import calcula_rsi
from indicadores.padroes_velas import engolfo_alta, piercing_line_alta
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class IndicatorWeights:
    """Pesos otimizados para cada categoria de indicador"""
    market_trend: float = 0.25      # 25% - Tendência de mercado
    structure: float = 0.20          # 20% - Estrutura de mercado
    fibonacci: float = 0.15          # 15% - Fibonacci
    wyckoff: float = 0.20            # 20% - Wyckoff/VSA
    didi_bollinger: float = 0.15     # 15% - Didi + Bollinger
    momentum: float = 0.05           # 5% - RSI e momentum

class AdvancedScoringSystem:
    """
    Sistema profissional de pontuação que combina múltiplos indicadores
    Score final: 0-100
    
    Categorias:
    - 90-100: EXCELENTE - Setup perfeito, alta probabilidade
    - 75-89: MUITO BOM - Setup forte, boa probabilidade
    - 60-74: BOM - Setup favorável, probabilidade moderada
    - 40-59: MODERADO - Sinais mistos, cautela
    - 20-39: FRACO - Poucos sinais, evitar
    - 0-19: PÉSSIMO - Sinais negativos, não entrar
    """
    
    def __init__(self):
        self.weights = IndicatorWeights()
        self.trend_analyzer = MarketTrendAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.fibonacci_analyzer = FibonacciAnalyzer()
        self.wyckoff_analyzer = WyckoffAnalyzer()
    
    def analyze_complete(self, simbolo: str) -> Dict[str, any]:
        """
        Análise completa profissional
        
        Returns:
            Dict com todos os indicadores e score final 0-100
        """
        try:
            # Buscar dados
            df = busca_velas(simbolo, '60', [9, 21, 200])  # 1 hora
            df = prepare_market_data(df, use_emas=True, emas_periods=[20, 50, 200])
            
            # ===== ANÁLISE DE TENDÊNCIA =====
            trend_analysis = self.trend_analyzer.analyze_trend(df)
            
            # ===== ANÁLISE DE ESTRUTURA =====
            structure_analysis = self.structure_analyzer.analyze_structure(df)
            
            # ===== ANÁLISE FIBONACCI =====
            fibonacci_analysis = self.fibonacci_analyzer.analyze_fibonacci(df)
            
            # ===== ANÁLISE WYCKOFF =====
            wyckoff_analysis = self.wyckoff_analyzer.analyze_wyckoff(df)
            
            # ===== DIDI + BOLLINGER (Sistema existente) =====
            didi_bollinger_score = self._analyze_didi_bollinger(df)
            
            # ===== MOMENTUM (RSI) =====
            momentum_score = self._analyze_momentum(df)
            
            # ===== CALCULAR SCORE FINAL =====
            final_score = self._calculate_final_score(
                trend_analysis,
                structure_analysis,
                fibonacci_analysis,
                wyckoff_analysis,
                didi_bollinger_score,
                momentum_score
            )
            
            # ===== CLASSIFICAÇÃO =====
            classification = self._classify_score(final_score)
            
            # ===== SINAIS PRINCIPAIS =====
            main_signals = self._extract_main_signals(
                trend_analysis,
                structure_analysis,
                fibonacci_analysis,
                wyckoff_analysis
            )
            
            # ===== RECOMENDAÇÃO =====
            recommendation = self._generate_recommendation(final_score, main_signals)
            
            return {
                'simbolo': simbolo,
                'score_final': final_score,
                'classification': classification,
                'recommendation': recommendation,
                'main_signals': main_signals,
                'details': {
                    'market_trend': trend_analysis,
                    'structure': structure_analysis,
                    'fibonacci': fibonacci_analysis,
                    'wyckoff': wyckoff_analysis,
                    'didi_bollinger': didi_bollinger_score,
                    'momentum': momentum_score
                },
                'price_current': df['fechamento'].iloc[-1]
            }
            
        except Exception as e:
            return {
                'simbolo': simbolo,
                'error': str(e),
                'score_final': 0
            }
    
    def _analyze_didi_bollinger(self, df: pd.DataFrame) -> Dict[str, any]:
        """Análise Didi + Bollinger (sistema existente)"""
        # Didi
        df['didi_curta'] = df['fechamento'].rolling(window=3).mean()
        df['didi_media'] = df['fechamento'].rolling(window=8).mean()
        df['didi_longa'] = df['fechamento'].rolling(window=20).mean()
        
        didi_curta = df['didi_curta'].iloc[-1]
        didi_media = df['didi_media'].iloc[-1]
        didi_longa = df['didi_longa'].iloc[-1]
        
        max_didi = max(didi_curta, didi_media, didi_longa)
        min_didi = min(didi_curta, didi_media, didi_longa)
        spread_didi = ((max_didi - min_didi) / max_didi) * 100
        
        # Bollinger
        df = bandas_bollinger(df, periodo=20, desvios=2)
        preco_atual = df['fechamento'].iloc[-1]
        bb_inferior = df['banda_inferior'].iloc[-1]
        bb_superior = df['banda_superior'].iloc[-1]
        
        posicao_bb = ((preco_atual - bb_inferior) / (bb_superior - bb_inferior)) * 100
        
        # Score
        score = 0
        if spread_didi < 3:
            score += 30  # Médias convergindo
        elif spread_didi < 5:
            score += 15
        
        if posicao_bb < 20:
            score += 30  # Zona de sobrevenda
        elif posicao_bb < 40:
            score += 15
        
        return {
            'score': min(score, 100),
            'spread_didi': spread_didi,
            'posicao_bb': posicao_bb
        }
    
    def _analyze_momentum(self, df: pd.DataFrame) -> Dict[str, any]:
        """Análise de Momentum (RSI)"""
        df['rsi'] = calcula_rsi(df, 14)
        rsi_atual = df['rsi'].iloc[-1]
        
        # Score baseado em RSI
        if rsi_atual < 25:
            score = 90  # Extremamente oversold
        elif rsi_atual < 30:
            score = 70  # Oversold
        elif rsi_atual < 40:
            score = 50  # Baixo
        elif rsi_atual > 75:
            score = 10  # Extremamente overbought
        elif rsi_atual > 70:
            score = 30  # Overbought
        else:
            score = 50  # Neutro
        
        return {
            'score': score,
            'rsi': rsi_atual
        }
    
    def _calculate_final_score(
        self,
        trend_analysis: Dict,
        structure_analysis: Dict,
        fibonacci_analysis: Dict,
        wyckoff_analysis: Dict,
        didi_bollinger: Dict,
        momentum: Dict
    ) -> float:
        """
        Calcula score final ponderado (0-100)
        """
        # Extrair scores individuais
        trend_score = trend_analysis['score']
        structure_score = structure_analysis['score']
        fibonacci_score = fibonacci_analysis['score']
        wyckoff_score = wyckoff_analysis['score']
        didi_bollinger_score = didi_bollinger['score']
        momentum_score = momentum['score']
        
        # Aplicar pesos
        final_score = (
            trend_score * self.weights.market_trend +
            structure_score * self.weights.structure +
            fibonacci_score * self.weights.fibonacci +
            wyckoff_score * self.weights.wyckoff +
            didi_bollinger_score * self.weights.didi_bollinger +
            momentum_score * self.weights.momentum
        )
        
        return round(final_score, 1)
    
    def _classify_score(self, score: float) -> Dict[str, str]:
        """Classifica o score"""
        if score >= 90:
            return {
                'level': 'EXCELENTE',
                'emoji': '🟢🟢🟢',
                'description': 'Setup perfeito - Alta probabilidade'
            }
        elif score >= 75:
            return {
                'level': 'MUITO BOM',
                'emoji': '🟢🟢',
                'description': 'Setup forte - Boa probabilidade'
            }
        elif score >= 60:
            return {
                'level': 'BOM',
                'emoji': '🟢',
                'description': 'Setup favorável - Probabilidade moderada'
            }
        elif score >= 40:
            return {
                'level': 'MODERADO',
                'emoji': '🟡',
                'description': 'Sinais mistos - Cautela'
            }
        elif score >= 20:
            return {
                'level': 'FRACO',
                'emoji': '⚪',
                'description': 'Poucos sinais - Evitar'
            }
        else:
            return {
                'level': 'PÉSSIMO',
                'emoji': '🔴',
                'description': 'Sinais negativos - Não entrar'
            }
    
    def _extract_main_signals(
        self,
        trend_analysis: Dict,
        structure_analysis: Dict,
        fibonacci_analysis: Dict,
        wyckoff_analysis: Dict
    ) -> List[str]:
        """Extrai sinais principais"""
        signals = []
        
        # Tendência
        if trend_analysis['score'] > 70:
            signals.append(f"Tendência {trend_analysis['trend']} Forte")
        
        # Estrutura
        if structure_analysis['bos']['detected']:
            signals.append(f"BOS {structure_analysis['bos']['type']}")
        
        if structure_analysis['choch']['detected']:
            signals.append(f"ChoCH {structure_analysis['choch']['type']}")
        
        # Fibonacci
        if fibonacci_analysis['score'] > 60:
            signals.append(fibonacci_analysis['interpretation'])
        
        # Wyckoff
        if wyckoff_analysis['spring']['detected']:
            signals.append("🚀 SPRING")
        
        if wyckoff_analysis['upthrust']['detected']:
            signals.append("⚠️ UPTHRUST")
        
        signals.extend(wyckoff_analysis['signals'][:3])  # Top 3 sinais
        
        return signals[:5]  # Máximo 5 sinais principais
    
    def _generate_recommendation(self, score: float, signals: List[str]) -> str:
        """Gera recomendação baseada no score"""
        if score >= 90:
            return "🟢 COMPRA FORTE RECOMENDADA - Confluência perfeita de múltiplos indicadores"
        elif score >= 75:
            return "🟢 COMPRA RECOMENDADA - Bons sinais de entrada"
        elif score >= 60:
            return "🟡 COMPRA VIÁVEL - Aguardar confirmação adicional recomendado"
        elif score >= 40:
            return "⏰ AGUARDAR - Sinais mistos, esperar melhores condições"
        elif score >= 20:
            return "❌ EVITAR - Poucos sinais favoráveis"
        else:
            return "🔴 NÃO ENTRAR - Condições desfavoráveis"


# Singleton instance
_scoring_system = None

def get_scoring_system() -> AdvancedScoringSystem:
    """Retorna instância singleton do sistema de scoring"""
    global _scoring_system
    if _scoring_system is None:
        _scoring_system = AdvancedScoringSystem()
    return _scoring_system
