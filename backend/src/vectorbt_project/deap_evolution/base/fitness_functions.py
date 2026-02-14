class TradingFitnessFunctions:
    """Coleção de funções de fitness para trading"""
    @staticmethod
    def return_drawdown_ratio(stats):
        return stats['Total Return [%]'] * (1 - stats['Max Drawdown [%]'] / 100)
    
    @staticmethod
    def sharpe_based(stats):
        return stats['Sharpe Ratio'] * (1 - stats['Max Drawdown [%]'] / 200)