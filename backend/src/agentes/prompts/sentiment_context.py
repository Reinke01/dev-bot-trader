import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from indicadores.fear_and_greed_index import obter_fear_greed_index, obter_fear_greed_mes_passado
from corretoras.funcoes_bybit import busca_lsr_open_interest
from textwrap import dedent

def format_sentiment_context(cripto, tempo_grafico="1h"):
    """
    Formata o contexto de sentimento do mercado usando o LSR, Open Interest e Fear and Greed Index.
    
    Returns:
        str: Contexto de sentimento formatado
    """
    
    if tempo_grafico in ["5", "15", "30"]:
        tempo_grafico = f"{tempo_grafico}min"
    elif tempo_grafico in ["1", "3"]:
        tempo_grafico = "5min"
    elif tempo_grafico in ["60", "120", "240"]:
        tempo_grafico = f"{int(tempo_grafico)/60}h"
    elif tempo_grafico == "D":
        tempo_grafico = "1d"
    elif tempo_grafico not in ["5min", "15min", "30min", '1h', '4h', '1d']:
        tempo_grafico = "1h"

    dados_7_dias = obter_fear_greed_index(7)
    dados_mes_passado = obter_fear_greed_mes_passado()
    dados_lsr = busca_lsr_open_interest(cripto, tempo_grafico, 10)
    
    return dedent(f"""# Contexto de sentimento do mercado:
## Long Short Ratio e Open Interest:
{dados_lsr.to_string(index=False) if not dados_lsr.empty else "Não há dados disponíveis"}

## Fear and Greed Index:
### Últimos 7 dias:
{dados_7_dias.to_string(index=False) if not dados_7_dias.empty else "Não há dados disponíveis"}

### 30 dias atrás:
{dados_mes_passado['data']}: {dados_mes_passado['valor'] if not dados_mes_passado.empty else "Não há dados disponíveis"}""")