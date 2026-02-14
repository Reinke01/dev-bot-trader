import requests
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def obter_fear_greed_index(dias: int = 7) -> pd.DataFrame:
    """
    Obtém o Fear and Greed Index para os últimos N dias.
    
    Args:
        dias (int): Número de dias para obter o indicador (padrão: 7)
        
    Returns:
        pd.DataFrame: DataFrame com colunas 'data' (DD/MM) e 'valor' do indicador
    """
    try:
        # Fazer requisição para a API
        url = f"https://api.alternative.me/fng/?limit={dias}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Verificar se há erro na resposta
        if data.get('metadata', {}).get('error'):
            logger.error(f"Erro na API: {data['metadata']['error']}")
            return pd.DataFrame(columns=['data', 'valor'])
        
        # Processar os dados
        resultado = []
        for item in data.get('data', []):
            # Converter timestamp para data no formato DD/MM
            timestamp = int(item['timestamp'])
            data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m')
            
            resultado.append({
                'data': data_formatada,
                'valor': f"{item['value_classification']} em {int(item['value'])}",
            })
        
        df = pd.DataFrame(resultado)
        logger.info(f"Fear and Greed Index obtido com sucesso para {len(df)} dias")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição HTTP: {e}")
        return pd.DataFrame(columns=['data', 'valor'])
    except ValueError as e:
        logger.error(f"Erro ao processar JSON: {e}")
        return pd.DataFrame(columns=['data', 'valor'])
    except Exception as e:
        logger.error(f"Erro inesperado ao obter Fear and Greed Index: {e}")
        return pd.DataFrame(columns=['data', 'valor'])


def obter_fear_greed_atual() -> pd.Series:
    """
    Obtém apenas o valor atual do Fear and Greed Index.
    
    Returns:
        pd.Series: Série com o valor atual do indicador
    """
    df = obter_fear_greed_index(1)
    return df.iloc[0] if not df.empty else pd.Series({'data': '', 'valor': ''})

def obter_fear_greed_mes_passado() -> pd.Series:
    """
    Obtém o Fear and Greed Index de 30 dias atrás.

    Returns:
        pd.Series: Série com o valor de 30 dias atrás do indicador
    """
    df = obter_fear_greed_index(30)
    return df.iloc[-1] if not df.empty else pd.Series({'data': '', 'valor': ''})


if __name__ == "__main__":
    # Teste da função
    print("Testando Fear and Greed Index...")
    
    # Obter últimos 7 dias
    resultado = obter_fear_greed_index(7)
    print(f"\nÚltimos 7 dias:")
    print(resultado)
    
    # Obter valor atual
    atual = obter_fear_greed_atual()
    print(f"\nValor atual:")
    print(f"{atual['data']} - {atual['valor']}")
    
    # Obter valor de 30 dias atrás
    mes_passado = obter_fear_greed_mes_passado()
    print(f"\n30 dias atrás:")
    print(f"{mes_passado['data']} - {mes_passado['valor']}")