from ...base import BaseDeapEvolver

class DoubleEMADeapEvolver(BaseDeapEvolver):
    """Implementação específica para Double EMA"""
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setup_deap()

    def setup_deap(self):
        """Configuração específica para Double EMA"""
        pass