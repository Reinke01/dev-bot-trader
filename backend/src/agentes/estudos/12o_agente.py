# Exemplo de agente de monitoramento de trades live com IA (sugestão do Claude no Cursor)
# Este agente não abre trades, apenas monitora os trades ativos, recomenda ajustes e realiza as ações recomendadas.

from agno.agent import Agent
from agno.models.groq import Groq
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entidades.estado_trade import EstadoDeTrade
from corretoras.funcoes_bybit import busca_velas, tem_trade_aberto
from indicadores.indicadores_osciladores import calcula_rsi, encontra_topos_e_fundos
from indicadores.bandas_bollinger import bandas_bollinger
from indicadores.topos_fundos import topos_fundos_duas_velas
from utils.logging import setup_logger

class AgenteMonitoramentoTrades:
    def __init__(self,
                cripto: str = "SOLUSDT",
                tempo_grafico: str = "15",
                subconta: int = 1,
                modelo_ia: str = "llama-3.3-70b-versatile"):
        
        self.cripto = cripto
        self.tempo_grafico = tempo_grafico
        self.subconta = subconta
        self.logger = setup_logger(f"agente_monitoring_{cripto}_{subconta}")
        
        # Configurar agente IA
        self.agent = Agent(
            model=Groq(
                id=modelo_ia,
                api_key=os.getenv('GROQ_API_KEY', "sua_chave_aqui")
            ),
            instructions=[
                "Você é um especialista em gestão de risco e análise de mercado em tempo real.",
                "Sua função é analisar condições de mercado para trades ativos e sugerir ajustes.",
                "Avalie: momentum, suportes/resistências, volume, padrões de reversão.",
                "Para cada análise, forneça uma recomendação em formato JSON:",
                "{'acao': 'manter'|'ajustar_stop'|'fechar_parcial'|'fechar_total',",
                " 'confianca': 0-100,",
                " 'novo_stop': valor_ou_null,",
                " 'novo_alvo': valor_ou_null,",
                " 'motivo': 'explicação detalhada'}"
            ],
            markdown=True
        )
        
        self.historico_analises = []
        self.ultima_analise = None
        
    def obter_dados_mercado(self) -> Dict:
        """Coleta dados abrangentes do mercado"""
        
        # Dados básicos de velas
        df = busca_velas(self.cripto, self.tempo_grafico, [5, 15, 21, 50])
        
        # Adicionar indicadores técnicos
        df = bandas_bollinger(df, periodo=20, desvios=2)
        df['rsi'] = calcula_rsi(df, periodo=14)
        
        # Padrões de topos e fundos
        df, fundos, topos = topos_fundos_duas_velas(df)
        
        # Topos e fundos por find_peaks
        topos_max, topos_fech, fundos_min, fundos_fech = encontra_topos_e_fundos(df)
        
        # Análise de volume
        df['volume_ma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        dados_mercado = {
            'preco_atual': df['fechamento'].iloc[-1],
            'ema_5': df['EMA_5'].iloc[-1],
            'ema_15': df['EMA_15'].iloc[-1],
            'ema_21': df['EMA_21'].iloc[-1], 
            'ema_50': df['EMA_50'].iloc[-1],
            'rsi': df['rsi'].iloc[-1],
            'banda_superior': df['banda_superior'].iloc[-1],
            'banda_inferior': df['banda_inferior'].iloc[-1],
            'volume_ratio': df['volume_ratio'].iloc[-1],
            'volatilidade': df['fechamento'].pct_change().rolling(20).std().iloc[-1] * 100,
            'tendencia_curto': self._analisar_tendencia(df, [5, 15]),
            'tendencia_medio': self._analisar_tendencia(df, [21, 50]),
            'topos_recentes': len(topos_max[-5:]) if len(topos_max) > 0 else 0,
            'fundos_recentes': len(fundos_min[-5:]) if len(fundos_min) > 0 else 0,
            'df_resumo': df.tail(10).to_dict('records')  # Últimas 10 velas
        }
        
        return dados_mercado
    
    def _analisar_tendencia(self, df: pd.DataFrame, emas: List[int]) -> str:
        """Analisa tendência baseada em EMAs"""
        ema_rapida = f'EMA_{emas[0]}'
        ema_lenta = f'EMA_{emas[1]}'
        
        preco = df['fechamento'].iloc[-1]
        ema_r = df[ema_rapida].iloc[-1]
        ema_l = df[ema_lenta].iloc[-1]
        
        if preco > ema_r > ema_l:
            return "alta"
        elif preco < ema_r < ema_l:
            return "baixa"
        else:
            return "lateral"
    
    def obter_status_trade(self) -> Tuple[EstadoDeTrade, float, float, float, float, float]:
        """Obtém status atual do trade"""
        return tem_trade_aberto(self.cripto, self.subconta)
    
    def analisar_condicoes_trade(self, dados_mercado: Dict, 
                                estado_trade: EstadoDeTrade,
                                preco_entrada: float,
                                preco_stop: float, 
                                preco_alvo: float) -> Dict:
        """Usa IA para analisar se deve ajustar o trade"""
        
        if estado_trade == EstadoDeTrade.DE_FORA:
            return {"acao": "sem_trade", "confianca": 100}
        
        # Calcular performance atual
        preco_atual = dados_mercado['preco_atual']
        if estado_trade == EstadoDeTrade.COMPRADO:
            pnl_percent = ((preco_atual - preco_entrada) / preco_entrada) * 100
        else:  # VENDIDO
            pnl_percent = ((preco_entrada - preco_atual) / preco_entrada) * 100
        
        # Preparar prompt para IA
        prompt = f"""
        ANÁLISE DE TRADE ATIVO - {self.cripto}
        
        Status do Trade:
        - Tipo: {'LONG' if estado_trade == EstadoDeTrade.COMPRADO else 'SHORT'}
        - Preço Entrada: {preco_entrada}
        - Preço Atual: {preco_atual}
        - Stop Loss: {preco_stop}
        - Take Profit: {preco_alvo}
        - P&L Atual: {pnl_percent:.2f}%
        
        Condições de Mercado:
        - RSI: {dados_mercado['rsi']:.2f}
        - Tendência Curto: {dados_mercado['tendencia_curto']}
        - Tendência Médio: {dados_mercado['tendencia_medio']}
        - Volume Ratio: {dados_mercado['volume_ratio']:.2f}
        - Volatilidade: {dados_mercado['volatilidade']:.2f}%
        
        EMAs:
        - EMA 5: {dados_mercado['ema_5']:.4f}
        - EMA 15: {dados_mercado['ema_15']:.4f} 
        - EMA 21: {dados_mercado['ema_21']:.4f}
        - EMA 50: {dados_mercado['ema_50']:.4f}
        
        Bandas de Bollinger:
        - Superior: {dados_mercado['banda_superior']:.4f}
        - Inferior: {dados_mercado['banda_inferior']:.4f}
        
        Padrões Recentes:
        - Topos últimas 5 velas: {dados_mercado['topos_recentes']}
        - Fundos últimas 5 velas: {dados_mercado['fundos_recentes']}
        
        Com base nessas informações, devo manter, ajustar ou fechar este trade?
        Considere especialmente sinais de reversão, momentum e gestão de risco.
        """
        
        try:
            response = self.agent.run(prompt)
            # Tentar extrair JSON da resposta
            analise = self._extrair_recomendacao(response.messages[-1].content)
            analise['timestamp'] = datetime.now().isoformat()
            analise['pnl_atual'] = pnl_percent
            
            return analise
            
        except Exception as e:
            self.logger.error(f"Erro na análise IA: {e}")
            return {
                "acao": "manter",
                "confianca": 0,
                "motivo": f"Erro na análise: {e}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _extrair_recomendacao(self, texto_resposta: str) -> Dict:
        """Extrai recomendação JSON da resposta da IA"""
        try:
            # Procurar por JSON na resposta
            import re
            json_pattern = r'\{.*?\}'
            matches = re.findall(json_pattern, texto_resposta, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
            
            # Se não encontrou JSON válido, fazer parsing manual
            if "fechar" in texto_resposta.lower():
                if "parcial" in texto_resposta.lower():
                    acao = "fechar_parcial"
                else:
                    acao = "fechar_total"
            elif "ajustar" in texto_resposta.lower():
                acao = "ajustar_stop"
            else:
                acao = "manter"
            
            return {
                "acao": acao,
                "confianca": 70,
                "motivo": texto_resposta[:200] + "...",
                "novo_stop": None,
                "novo_alvo": None
            }
            
        except Exception as e:
            return {
                "acao": "manter",
                "confianca": 0,
                "motivo": f"Erro ao interpretar resposta: {e}"
            }
    
    def executar_recomendacao(self, recomendacao: Dict) -> bool:
        """Executa a recomendação do agente (implementar conforme necessário)"""
        
        acao = recomendacao.get('acao')
        confianca = recomendacao.get('confianca', 0)
        
        # Só executar se confiança for alta
        if confianca < 70:
            self.logger.info(f"Confiança baixa ({confianca}%), não executando ação")
            return False
        
        self.logger.info(f"Executando recomendação: {acao}")
        
        if acao == "fechar_total":
            # Implementar fechamento total
            self.logger.info("AÇÃO: Fechamento total recomendado")
            # TODO: Implementar fechamento via API
            
        elif acao == "fechar_parcial":
            # Implementar fechamento parcial
            self.logger.info("AÇÃO: Fechamento parcial recomendado")
            # TODO: Implementar fechamento parcial
            
        elif acao == "ajustar_stop":
            novo_stop = recomendacao.get('novo_stop')
            if novo_stop:
                self.logger.info(f"AÇÃO: Ajustando stop para {novo_stop}")
                # TODO: Implementar ajuste de stop
        
        return True
    
    def monitorar(self, intervalo_segundos: int = 30):
        """Loop principal de monitoramento"""
        
        self.logger.info(f"Iniciando monitoramento de {self.cripto} (subconta {self.subconta})")
        
        while True:
            try:
                # Verificar se há trade ativo
                estado_trade, preco_entrada, preco_stop, preco_alvo = self.obter_status_trade()
                
                if estado_trade != EstadoDeTrade.DE_FORA:
                    # Coletar dados de mercado
                    dados_mercado = self.obter_dados_mercado()
                    
                    # Analisar com IA
                    analise = self.analisar_condicoes_trade(
                        dados_mercado, estado_trade, preco_entrada, preco_stop, preco_alvo
                    )
                    
                    # Salvar análise
                    self.historico_analises.append(analise)
                    self.ultima_analise = analise
                    
                    # Log da análise
                    self.logger.info(f"""
                    ANÁLISE TRADE:
                    Ação: {analise['acao']}
                    Confiança: {analise['confianca']}%
                    P&L: {analise.get('pnl_atual', 0):.2f}%
                    Motivo: {analise['motivo'][:100]}...
                    """)
                    
                    # Executar se necessário
                    if analise['acao'] != 'manter':
                        self.executar_recomendacao(analise)
                
                else:
                    self.logger.debug("Nenhum trade ativo encontrado")
                
                time.sleep(intervalo_segundos)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(intervalo_segundos)

# Função para iniciar o agente
def iniciar_agente_monitoramento(cripto: str = "SOLUSDT", 
                                subconta: int = 1,
                                intervalo: int = 30):
    
    agente = AgenteMonitoramentoTrades(cripto=cripto, subconta=subconta)
    agente.monitorar(intervalo_segundos=intervalo)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--cripto', default='SOLUSDT')
    parser.add_argument('--subconta', type=int, default=1)
    parser.add_argument('--intervalo', type=int, default=30)
    
    args = parser.parse_args()
    
    iniciar_agente_monitoramento(
        cripto=args.cripto,
        subconta=args.subconta, 
        intervalo=args.intervalo
    )


# Exemplos de uso:

# Monitorar SOLUSDT na subconta 1 a cada 30 segundos
# python src/agentes/agente_monitoramento_trades.py --cripto SOLUSDT --subconta 1 --intervalo 30

# Monitorar múltiplas posições
# python src/agentes/agente_monitoramento_trades.py --cripto BTCUSDT --subconta 2 --intervalo 60