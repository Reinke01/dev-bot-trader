import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from corretoras.funcoes_bybit import busca_pnl
from textwrap import dedent

def format_trades_pnl(subconta, quantidade=20):
    trades = busca_pnl(subconta)
    
    # Trata o caso de DataFrame vazio
    if trades.empty:
        return dedent("""
        # Trades e PnL dos últimos trades:
        ## Nenhum trade fechado encontrado.
        
        ## PnL:
        0.00
        
        ## Taxa de acerto:
        ### Não há dados disponíveis""")
    
    total_trades = len(trades)
    total_positivos = (trades['pnl'] > 0).sum()
    taxa_acerto_total = (total_positivos / total_trades * 100) if total_trades > 0 else 0

    ultimos_trades = trades.head(quantidade)
    ultimos_positivos = (ultimos_trades['pnl'] > 0).sum()
    taxa_acerto_ultimos = (ultimos_positivos / len(ultimos_trades) * 100) if len(ultimos_trades) > 0 else 0
    
    return dedent(f"""
# Trades e PnL dos últimos {quantidade} trades:
## Trades:
{trades.head(quantidade).to_string(index=False)}

## PnL:
{round(sum(trades['pnl'].head(quantidade)), 2)}

## Taxa de acerto:
### Últimos {quantidade} trades: {taxa_acerto_ultimos:.2f}%
### Últimos {total_trades} trades: {taxa_acerto_total:.2f}%""")