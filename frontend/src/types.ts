export interface LogEntry {
    timestamp: string;
    message: string;
    level: string;
    bot_id?: string;
}

export interface BotSummary {
    bot_id: string;
    status: string;
    cripto: string;
    tempo_grafico: string;
    subconta: number;
    last_update?: string;
    is_simulator: boolean;
    ema_rapida_compra: number;
    ema_lenta_compra: number;
    ema_rapida_venda: number;
    ema_lenta_venda: number;
    lado_operacao: string;
    risco_por_operacao: number;
}

export interface ScannerResult {
    symbol: string;
    price: number;
    score: number;
    rsi: number;
    factors: {
        trend_htf: boolean;
        trend_mtf: boolean;
        rsi_zone: boolean;
        vol_surge: boolean;
        setup_prox: boolean;
    };
    last_update: string;
}

export interface BotConfig {
    subconta: number;
    tempo_grafico: string;
    lado_operacao: string;
    frequencia_agente_horas: number;
    executar_agente_no_start: boolean;
    ema_rapida_compra: number;
    ema_lenta_compra: number;
    ema_rapida_venda: number;
    ema_lenta_venda: number;
    risco_por_operacao: number;
    is_simulator: boolean;
}

export interface TradeHistoryItem {
    bot_id: string;
    symbol: string;
    side: 'compra' | 'venda';
    entry_price: number;
    exit_price: number;
    pnl: number;
    pnl_percent: number;
    closed_at: string;
    result: 'target' | 'stop' | 'manual';
}

export interface PerformanceStats {
    totalPnL: number;
    winRate: number;
    totalTrades: number;
    profitFactor: number;
}

export interface GlobalConfig {
    bybitKey: string;
    bybitSecret: string;
    webhookUrl: string;
    autoDap: boolean;
    autoDapInterval: number;
    maxConcurrentBots: number;
    globalDailyLossLimit: number;
    riskShieldEnabled: boolean;
    aiKnowledgePath: string;
    terminalMode: 'essential' | 'technical';
}

export interface OptimizationResult {
    parameters: {
        ema_short: number;
        ema_long: number;
        stop_candles: number;
        risk_reward: number;
    };
    metrics: {
        return: number;
        drawdown: number;
        win_rate: number;
        trades: number;
        fitness: number;
        profit_factor?: number;
    };
}
