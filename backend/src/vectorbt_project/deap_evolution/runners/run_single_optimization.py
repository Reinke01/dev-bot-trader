def run_optimization(strategy_name, preset='quick', **kwargs):
    """Executa otimização para uma única estratégia"""
    config = load_config(preset)
    evolver = get_evolver_class(strategy_name)(config)
    results = evolver.run()
    save_results(results)