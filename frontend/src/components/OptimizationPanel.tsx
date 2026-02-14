import { memo, useState, useEffect } from 'react';
import { Sparkles, TrendingUp, ShieldAlert, Check, Play, Loader2 } from 'lucide-react';
import type { OptimizationResult } from '../types';

interface OptimizationPanelProps {
    symbol: string;
    onApply: (params: OptimizationResult['parameters']) => void;
}

export const OptimizationPanel = memo(({ symbol, onApply }: OptimizationPanelProps) => {
    const [results, setResults] = useState<OptimizationResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchOptimization = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const res = await fetch(`http://localhost:8000/api/v1/optimization/top/${symbol}?days=7`);
            const data = await res.json();
            if (data.success) {
                setResults(data.results);
            } else {
                setError(data.message || "Falha ao obter otimização.");
            }
        } catch (err) {
            setError("Erro de conexão com o servidor.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (symbol) fetchOptimization();
    }, [symbol]);

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-primary/20 rounded-lg">
                        <Sparkles className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                        <h4 className="text-[10px] font-bold text-white uppercase tracking-wider">Dynamic Asset Profiler</h4>
                        <p className="text-[9px] text-gray-500 uppercase font-mono">Top Alpha Configs (7 Days)</p>
                    </div>
                </div>
                <button
                    onClick={fetchOptimization}
                    disabled={isLoading}
                    className="p-1.5 hover:bg-white/5 rounded-lg text-gray-500 hover:text-primary transition-all"
                >
                    {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                </button>
            </div>

            {error ? (
                <div className="p-3 rounded-xl bg-danger/10 border border-danger/20 flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-danger" />
                    <p className="text-[10px] text-danger font-medium">{error}</p>
                </div>
            ) : isLoading ? (
                <div className="space-y-2">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-16 bg-white/5 rounded-xl animate-pulse" />
                    ))}
                </div>
            ) : results.length > 0 ? (
                <div className="space-y-2">
                    {results.map((res, idx) => (
                        <div
                            key={idx}
                            onClick={() => onApply(res.parameters)}
                            className="group p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer relative overflow-hidden"
                        >
                            <div className="flex items-center justify-between relative z-10">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <span className="text-[10px] font-black text-primary">EMA {res.parameters.ema_short}/{res.parameters.ema_long}</span>
                                        <span className="px-1.5 py-0.5 rounded bg-white/5 text-[8px] font-bold text-gray-400 uppercase">Stop: {res.parameters.stop_candles}</span>
                                        <span className="px-1.5 py-0.5 rounded bg-white/5 text-[8px] font-bold text-gray-400 uppercase">RR: {res.parameters.risk_reward}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className="flex items-center gap-1">
                                            <TrendingUp className="w-3 h-3 text-success" />
                                            <span className="text-xs font-bold text-success">+{res.metrics.return}%</span>
                                        </div>
                                        <div className="text-[9px] text-gray-500">
                                            WR: <span className="text-gray-300 font-bold">{res.metrics.win_rate}%</span>
                                        </div>
                                        <div className="text-[9px] text-gray-500">
                                            Fitness: <span className="text-primary font-bold">{res.metrics.fitness}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Check className="w-4 h-4 text-primary" />
                                </div>
                            </div>
                            {/* Ranking Badge */}
                            <div className="absolute -right-1 -top-1 px-2 py-0.5 bg-primary/20 text-primary text-[8px] font-black rounded-bl-lg border-l border-b border-primary/30">
                                #{idx + 1}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="p-8 text-center border-2 border-dashed border-white/5 rounded-2xl">
                    <p className="text-[10px] text-gray-600 uppercase font-black">Nenhum perfil otimizado ainda</p>
                </div>
            )}
        </div>
    );
});

OptimizationPanel.displayName = 'OptimizationPanel';
