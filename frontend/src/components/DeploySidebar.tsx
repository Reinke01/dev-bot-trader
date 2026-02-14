import { memo, useCallback } from 'react';
import { X, Zap, TrendingUp, TrendingDown, ShieldCheck, ArrowRight, FlaskConical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { BotConfig, OptimizationResult } from '../types';
import { OptimizationPanel } from './OptimizationPanel';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface DeploySidebarProps {
    selectedSymbol: string | null;
    setSelectedSymbol: (symbol: string | null) => void;
    config: BotConfig;
    setConfig: (config: BotConfig) => void;
    errors: Record<string, string>;
    isDeploying: boolean;
    deployBot: () => void;
}

export const DeploySidebar = memo(({
    selectedSymbol,
    setSelectedSymbol,
    config,
    setConfig,
    errors,
    isDeploying,
    deployBot
}: DeploySidebarProps) => {
    const handleApplyOptimization = useCallback((params: OptimizationResult['parameters']) => {
        setConfig({
            ...config,
            ema_rapida_compra: params.ema_short,
            ema_lenta_compra: params.ema_long,
            ema_rapida_venda: params.ema_short,
            ema_lenta_venda: params.ema_long
        });
    }, [config, setConfig]);

    return (
        <AnimatePresence>
            {selectedSymbol && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setSelectedSymbol(null)}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
                    />
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed right-0 top-0 h-full w-[400px] glass border-l border-primary/20 z-[101] flex flex-col shadow-2xl overflow-hidden"
                    >
                        <div className="p-8 border-b border-white/5 flex items-center justify-between bg-primary/5">
                            <div>
                                <h2 className="text-xl font-bold text-primary flex items-center gap-2">
                                    <Zap className="w-5 h-5 fill-primary" />
                                    Deploy System
                                </h2>
                                <p className="text-xs text-secondary font-mono uppercase tracking-widest">{selectedSymbol}</p>
                            </div>
                            <button
                                onClick={() => setSelectedSymbol(null)}
                                className="p-2 hover:bg-white/5 rounded-full transition-colors"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-8 space-y-6">
                            <div>
                                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-2">Bot Settings</label>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1.5">
                                        <span className="text-[9px] text-gray-400 uppercase">Subaccount</span>
                                        <input
                                            type="number"
                                            value={config.subconta}
                                            onChange={(e) => setConfig({ ...config, subconta: parseInt(e.target.value) })}
                                            className={cn(
                                                "w-full bg-white/5 border rounded-lg px-3 py-2 text-sm focus:border-primary outline-none transition-all",
                                                errors.subconta ? "border-danger" : "border-white/10"
                                            )}
                                        />
                                        {errors.subconta && <p className="text-[9px] text-danger">{errors.subconta}</p>}
                                    </div>
                                    <div className="space-y-1.5">
                                        <span className="text-[9px] text-gray-400 uppercase">Timeframe</span>
                                        <select
                                            value={config.tempo_grafico}
                                            onChange={(e) => setConfig({ ...config, tempo_grafico: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm focus:border-primary outline-none transition-all"
                                        >
                                            <option value="1">1m</option>
                                            <option value="5">5m</option>
                                            <option value="15">15m</option>
                                            <option value="60">1h</option>
                                            <option value="240">4h</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            {selectedSymbol && (
                                <OptimizationPanel
                                    symbol={selectedSymbol}
                                    onApply={handleApplyOptimization}
                                />
                            )}

                            <div className="space-y-4">
                                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block">EMA Strategy</label>
                                <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-4">
                                    <div className="space-y-2">
                                        <div className="flex items-center gap-2 text-success text-[10px] font-bold uppercase transition-colors">
                                            <TrendingUp className="w-3 h-3" /> Buy Config
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
                                            <input
                                                placeholder="Fast"
                                                type="number"
                                                value={config.ema_rapida_compra}
                                                onChange={(e) => setConfig({ ...config, ema_rapida_compra: parseInt(e.target.value) })}
                                                className="bg-black/40 border border-white/5 rounded px-2 py-1.5 text-xs outline-none focus:border-success/50"
                                            />
                                            <input
                                                placeholder="Slow"
                                                type="number"
                                                value={config.ema_lenta_compra}
                                                onChange={(e) => setConfig({ ...config, ema_lenta_compra: parseInt(e.target.value) })}
                                                className="bg-black/40 border border-white/5 rounded px-2 py-1.5 text-xs outline-none focus:border-success/50"
                                            />
                                        </div>
                                        {(errors.ema_rapida_compra || errors.ema_lenta_compra) && (
                                            <p className="text-[9px] text-danger">{errors.ema_rapida_compra || errors.ema_lenta_compra}</p>
                                        )}
                                    </div>

                                    <div className="h-[1px] bg-white/5" />

                                    <div className="space-y-2">
                                        <div className="flex items-center gap-2 text-danger text-[10px] font-bold uppercase">
                                            <TrendingDown className="w-3 h-3" /> Sell Config
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
                                            <input
                                                placeholder="Fast"
                                                type="number"
                                                value={config.ema_rapida_venda}
                                                onChange={(e) => setConfig({ ...config, ema_rapida_venda: parseInt(e.target.value) })}
                                                className="bg-black/40 border border-white/5 rounded px-2 py-1.5 text-xs outline-none focus:border-danger/50"
                                            />
                                            <input
                                                placeholder="Slow"
                                                type="number"
                                                value={config.ema_lenta_venda}
                                                onChange={(e) => setConfig({ ...config, ema_lenta_venda: parseInt(e.target.value) })}
                                                className="bg-black/40 border border-white/5 rounded px-2 py-1.5 text-xs outline-none focus:border-danger/50"
                                            />
                                        </div>
                                        {(errors.ema_rapida_venda || errors.ema_lenta_venda) && (
                                            <p className="text-[9px] text-danger">{errors.ema_rapida_venda || errors.ema_lenta_venda}</p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-4">Risk Exposure</label>
                                <input
                                    type="range" min="0.005" max="0.08" step="0.005"
                                    value={config.risco_por_operacao}
                                    onChange={(e) => setConfig({ ...config, risco_por_operacao: parseFloat(e.target.value) })}
                                    className="w-full accent-primary h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer"
                                />
                                <div className="flex justify-between text-[10px] items-center mt-3">
                                    <span className="text-gray-500">Very Low (0.5%)</span>
                                    <span className="text-primary font-bold text-sm bg-primary/10 px-2 py-1 rounded">{(config.risco_por_operacao * 100).toFixed(1)}%</span>
                                    <span className="text-gray-500">Very High (8%)</span>
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block">Execution Mode</label>
                                    <span className={cn(
                                        "text-[9px] px-2 py-0.5 rounded font-bold uppercase",
                                        config.is_simulator ? "bg-warning/20 text-warning" : "bg-success/20 text-success"
                                    )}>
                                        {config.is_simulator ? 'Simulator' : 'Live Trade'}
                                    </span>
                                </div>
                                <button
                                    onClick={() => setConfig({ ...config, is_simulator: !config.is_simulator })}
                                    className={cn(
                                        "w-full p-4 rounded-xl border transition-all flex items-center justify-between group",
                                        config.is_simulator
                                            ? "bg-warning/10 border-warning/30 hover:bg-warning/20"
                                            : "bg-white/5 border-white/10 hover:bg-white/10"
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={cn(
                                            "w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
                                            config.is_simulator ? "bg-warning/20 text-warning" : "bg-white/10 text-gray-400"
                                        )}>
                                            <FlaskConical className="w-5 h-5" />
                                        </div>
                                        <div className="text-left">
                                            <p className="text-sm font-bold text-white leading-tight">Simulator Mode</p>
                                            <p className="text-[10px] text-gray-500">Virtual execution without risk</p>
                                        </div>
                                    </div>
                                    <div className={cn(
                                        "w-12 h-6 rounded-full relative transition-colors",
                                        config.is_simulator ? "bg-warning" : "bg-white/10"
                                    )}>
                                        <div className={cn(
                                            "absolute top-1 w-4 h-4 bg-white rounded-full transition-all",
                                            config.is_simulator ? "left-7" : "left-1"
                                        )} />
                                    </div>
                                </button>
                            </div>

                            <div className="p-4 rounded-xl bg-warning/5 border border-warning/20">
                                <div className="flex items-center gap-2 text-warning text-xs font-bold mb-1">
                                    <ShieldCheck className="w-4 h-4" /> Safety Check
                                </div>
                                <p className="text-[10px] text-gray-400 italic">Ensure your subaccount has sufficient margin for the selected risk level.</p>
                            </div>
                        </div>

                        <div className="p-8 bg-black/40 border-t border-white/5 space-y-4">
                            {errors.general && (
                                <div className="p-3 bg-danger/10 border border-danger/20 rounded-lg text-danger text-[10px] font-bold">
                                    {errors.general}
                                </div>
                            )}
                            <button
                                onClick={deployBot}
                                disabled={isDeploying}
                                className={cn(
                                    "w-full py-4 rounded-xl font-bold uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-3",
                                    isDeploying
                                        ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                                        : "bg-primary text-background hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_30px_rgba(255,215,0,0.2)]"
                                )}
                            >
                                {isDeploying ? (
                                    <div className="w-5 h-5 border-2 border-background/30 border-t-background rounded-full animate-spin" />
                                ) : (
                                    <>
                                        Initiate Pulse
                                        <ArrowRight className="w-5 h-5" />
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.div>
                </>
            )
            }
        </AnimatePresence >
    );
});

DeploySidebar.displayName = 'DeploySidebar';
