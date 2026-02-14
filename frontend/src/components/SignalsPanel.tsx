import { Zap, Check, TrendingUp, Sparkles, AlertCircle, FlaskConical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { ScannerResult } from '../types';
import { memo } from 'react';

interface SignalsPanelProps {
    signals: ScannerResult[];
    onApprove: (symbol: string, isSimulator?: boolean) => void;
    isDeploying: boolean;
    terminalMode: 'essential' | 'technical';
}

export const SignalsPanel = memo(({ signals, onApprove, isDeploying, terminalMode }: SignalsPanelProps) => {
    const isTechnical = terminalMode === 'technical';
    return (
        <div className="glass rounded-2xl flex flex-col overflow-hidden border border-white/5">
            <div className="p-5 border-b border-white/5 bg-gradient-to-r from-success/10 to-transparent flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-success/20 rounded-lg">
                        <Zap className="w-5 h-5 text-success" />
                    </div>
                    <div>
                        <h3 className="font-bold text-sm text-white uppercase tracking-wider">AI Opportunities</h3>
                        <p className="text-[10px] text-gray-500 font-mono">TOP 10 QUANT SIGNALS</p>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-success/10 rounded-full border border-success/20">
                    <Sparkles className="w-3 h-3 text-success animate-pulse" />
                    <span className="text-[10px] text-success font-bold uppercase">Live Analysis</span>
                </div>
            </div>

            <div className="p-4 space-y-3 max-h-[400px] overflow-y-auto custom-scrollbar">
                <AnimatePresence mode="popLayout">
                    {signals.length > 0 ? (
                        signals.map((signal) => (
                            <motion.div
                                key={signal.symbol}
                                layout
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-success/30 transition-all group"
                            >
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-black/40 flex items-center justify-center border border-white/10 group-hover:border-success/50 transition-colors">
                                            <span className="text-[10px] font-black text-white">{signal.symbol.replace('USDT', '')}</span>
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-bold text-white">{signal.symbol}</span>
                                                <span className="text-[10px] px-1.5 py-0.5 bg-success/20 text-success rounded font-mono">
                                                    Score {signal.score}/5
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-2 mt-0.5">
                                                <TrendingUp className="w-3 h-3 text-gray-500" />
                                                <span className="text-[10px] text-gray-500 font-mono">${signal.price.toLocaleString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => onApprove(signal.symbol, true)}
                                            disabled={isDeploying}
                                            className="h-10 px-3 bg-warning text-background rounded-xl font-bold text-[10px] uppercase tracking-tighter hover:scale-105 active:scale-95 transition-all flex items-center gap-2 shadow-lg shadow-warning/20 disabled:opacity-50"
                                            title="Executar em modo simulador"
                                        >
                                            <FlaskConical className="w-3 h-3" />
                                            Simular
                                        </button>
                                        <button
                                            onClick={() => onApprove(signal.symbol, false)}
                                            disabled={isDeploying}
                                            className="h-10 px-3 bg-success text-background rounded-xl font-bold text-[10px] uppercase tracking-tighter hover:scale-105 active:scale-95 transition-all flex items-center gap-2 shadow-lg shadow-success/20 disabled:opacity-50"
                                        >
                                            <Check className="w-4 h-4" />
                                            Aprovar
                                        </button>
                                    </div>
                                </div>

                                {isTechnical && (
                                    <div className="grid grid-cols-5 gap-1">
                                        {Object.entries(signal.factors).map(([key, active]) => (
                                            <div
                                                key={key}
                                                title={key.replace('_', ' ').toUpperCase()}
                                                className={`h-1 rounded-full ${active ? 'bg-success' : 'bg-white/10'}`}
                                            />
                                        ))}
                                    </div>
                                )}
                            </motion.div>
                        ))
                    ) : (
                        <div className="py-10 flex flex-col items-center justify-center text-center">
                            <AlertCircle className="w-8 h-8 text-gray-600 mb-3" />
                            <p className="text-xs text-gray-500">Buscando oportunidades de alta probabilidade...</p>
                        </div>
                    )}
                </AnimatePresence>
            </div>
        </div >
    );
});

SignalsPanel.displayName = 'SignalsPanel';
