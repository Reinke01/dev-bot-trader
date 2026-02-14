class BaseDeapEvolver:
    """Classe base para todos os otimizadores DEAP"""
    def __init__(self):
        self.toolbox = None
        self.stats = None
        self.hof = None
    
    def setup_deap(self):
        """Template para configuração do DEAP"""
        pass
    
    def evaluate(self):
        """Template para função de avaliação"""
        pass