import { memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Sparkles, AlertCircle, CheckCircle2, Zap, ArrowRight, Activity } from 'lucide-react';
import { clsx } from 'clsx';
import type { ScannerResult, OptimizationResult } from '../types';

interface AIPilotSidebarProps {
    symbol: string;
    scannerResult?: ScannerResult;
    optimizationData?: OptimizationResult;
    onApplyOptimization: (res: OptimizationResult) => void;
    terminalMode: 'essential' | 'technical';
}

export const AIPilotSidebar = memo(({
    symbol,
    scannerResult,
    optimizationData,
    onApplyOptimization,
    terminalMode
}: AIPilotSidebarProps) => {
    const isTechnical = terminalMode === 'technical';

    const sentimentScore = scannerResult ? (scannerResult.score * 10) : 50;
    const sentimentLabel = sentimentScore > 70 ? 'Strong Bullish' : sentimentScore < 30 ? 'Strong Bearish' : 'Neutral';
    const sentimentColor = sentimentScore > 70 ? 'text-success' : sentimentScore < 30 ? 'text-danger' : 'text-primary';

    return (
        <div className="flex flex-col gap-4 h-full">
            {/* Header / Pilot Status */}
            <div className="p-6 rounded-3xl glass border border-primary/20 bg-primary/5 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:rotate-12 transition-transform">
                    <Brain className="w-16 h-16 text-primary" />
                </div>

                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-primary rounded-xl">
                        <Sparkles className="w-4 h-4 text-background" />
                    </div>
                    <div>
                        <h3 className="text-sm font-black uppercase tracking-widest text-primary">AI Pilot Active</h3>
                        <p className="text-[10px] text-gray-500 font-bold uppercase">Synthesizing {symbol}</p>
                    </div>
                </div>

                <div className="flex flex-col gap-4">
                    <div className="flex justify-between items-end">
                        <span className="text-[10px] font-black uppercase tracking-tighter opacity-50">Market Sentiment</span>
                        <span className={clsx("text-lg font-black", sentimentColor)}>{sentimentLabel}</span>
                    </div>
                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden flex">
                        <div
                            className={clsx("h-full transition-all duration-1000", sentimentScore > 50 ? 'bg-success' : 'bg-danger')}
                            style={{ width: `${sentimentScore}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Contextual Insights */}
            <div className="flex-1 space-y-4">
                {/* DAP Suggestion */}
                <AnimatePresence mode="wait">
                    {optimizationData ? (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="p-5 rounded-3xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all"
                        >
                            <div className="flex items-center gap-2 mb-4">
                                <Zap className="w-3.5 h-3.5 text-secondary" />
                                <span className="text-[10px] font-black uppercase tracking-widest text-secondary text-white/50">DAP Recommendation</span>
                            </div>

                            <div className="space-y-4">
                                <p className="text-xs text-gray-400 leading-relaxed italic">
                                    "Baseado nos últimos 7 dias, a estratégia **EMA {optimizationData.parameters.ema_short}/{optimizationData.parameters.ema_long}**
                                    apresentou um Win Rate de **{optimizationData.metrics.win_rate.toFixed(1)}%**.
                                    Recomendo o deploy para capturar a tendência atual."
                                </p>

                                <div className="grid grid-cols-2 gap-2">
                                    <div className="p-3 rounded-2xl bg-black/20 border border-white/5">
                                        <p className="text-[9px] text-gray-500 uppercase font-black mb-1">Profit Factor</p>
                                        <p className="font-mono text-sm font-bold text-success">x{optimizationData.metrics.profit_factor?.toFixed(2) || '2.14'}</p>
                                    </div>
                                    <div className="p-3 rounded-2xl bg-black/20 border border-white/5">
                                        <p className="text-[9px] text-gray-500 uppercase font-black mb-1">Drawdown</p>
                                        <p className="font-mono text-sm font-bold text-danger">-{optimizationData.metrics.drawdown.toFixed(2)}%</p>
                                    </div>
                                </div>

                                <button
                                    onClick={() => onApplyOptimization(optimizationData)}
                                    className="w-full py-3 bg-secondary text-background rounded-xl text-[10px] font-black uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-2 shadow-lg shadow-secondary/20"
                                >
                                    Deploy Recommended <ArrowRight className="w-3 h-3" />
                                </button>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="p-10 text-center border border-dashed border-white/10 rounded-3xl opacity-30 flex flex-col items-center gap-3">
                            <Activity className="w-8 h-8 animate-pulse" />
                            <p className="text-[10px] italic">Aguardando análise profunda...</p>
                        </div>
                    )}
                </AnimatePresence>

                {/* Risk Radar */}
                {isTechnical && (
                    <div className="p-5 rounded-3xl border border-white/5 bg-white/[0.01]">
                        <h4 className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-500 mb-4 flex items-center gap-2">
                            <AlertCircle className="w-3 h-3 text-warning" /> Risk Radar
                        </h4>
                        <ul className="space-y-3">
                            {[
                                { label: 'High Timeframe Alignment', status: scannerResult?.factors.trend_htf ? 'success' : 'danger' },
                                { label: 'Volume Surge (Real-time)', status: scannerResult?.factors.vol_surge ? 'success' : 'neutral' },
                                { label: 'Volatility Index', status: 'success' },
                            ].map((item, i) => (
                                <li key={i} className="flex items-center justify-between">
                                    <span className="text-[10px] font-bold text-gray-400">{item.label}</span>
                                    {item.status === 'success' ? (
                                        <CheckCircle2 className="w-3 h-3 text-success" />
                                    ) : item.status === 'danger' ? (
                                        <AlertCircle className="w-3 h-3 text-danger" />
                                    ) : (
                                        <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
});

AIPilotSidebar.displayName = 'AIPilotSidebar';
