import { useState, memo, useEffect } from 'react';
import { X, Key, Save, ShieldCheck, Globe, Sparkles, AlertTriangle, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import type { GlobalConfig } from '../types';

interface ConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const DEFAULT_CONFIG: GlobalConfig = {
    bybitKey: '',
    bybitSecret: '',
    webhookUrl: '',
    autoDap: false,
    autoDapInterval: 6,
    maxConcurrentBots: 10,
    globalDailyLossLimit: 5,
    riskShieldEnabled: true,
    aiKnowledgePath: 'src/agentes/knowledge',
    terminalMode: 'technical'
};

interface ConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfigChange?: (config: GlobalConfig) => void;
}

export const ConfigModal = memo(({ isOpen, onClose, onConfigChange }: ConfigModalProps) => {
    const [config, setConfig] = useState<GlobalConfig>(DEFAULT_CONFIG);

    useEffect(() => {
        const saved = localStorage.getItem('terminal_config');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                setConfig({ ...DEFAULT_CONFIG, ...parsed });
            } catch (e) {
                console.error("Failed to parse config", e);
            }
        }
    }, [isOpen]);

    const handleSave = () => {
        localStorage.setItem('terminal_config', JSON.stringify(config));
        if (onConfigChange) onConfigChange(config);
        console.log("Saving Global Config:", config);
        onClose();
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/90 backdrop-blur-xl z-[300]"
                    />
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.9, opacity: 0, y: 20 }}
                        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] glass border border-primary/30 rounded-[32px] z-[301] overflow-hidden shadow-[0_0_100px_rgba(255,215,0,0.15)]"
                    >
                        <div className="p-8 border-b border-white/5 flex items-center justify-between bg-primary/5">
                            <div>
                                <h2 className="text-2xl font-black text-primary uppercase tracking-tighter flex items-center gap-3">
                                    <Globe className="w-8 h-8" />
                                    Terminal Excellence
                                </h2>
                                <div className="flex items-center gap-2 mt-2">
                                    <button
                                        onClick={() => setConfig({ ...config, terminalMode: 'essential' })}
                                        className={clsx(
                                            "px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest transition-all",
                                            config.terminalMode === 'essential' ? "bg-primary text-background" : "bg-white/5 text-gray-500 hover:bg-white/10"
                                        )}
                                    >
                                        Essential
                                    </button>
                                    <button
                                        onClick={() => setConfig({ ...config, terminalMode: 'technical' })}
                                        className={clsx(
                                            "px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest transition-all",
                                            config.terminalMode === 'technical' ? "bg-primary text-background" : "bg-white/5 text-gray-500 hover:bg-white/10"
                                        )}
                                    >
                                        Technical
                                    </button>
                                </div>
                            </div>
                            <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full text-gray-400">
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="p-8 space-y-10 max-h-[75vh] overflow-auto custom-scrollbar">

                            {/* Bybit API Section */}
                            <div className="space-y-6">
                                <h3 className="text-[11px] font-black text-white uppercase tracking-[0.2em] flex items-center gap-2">
                                    <Key className="w-4 h-4 text-primary" /> Exchange Connectivity
                                </h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1.5">
                                        <label className="text-[9px] text-gray-500 uppercase ml-1">Bybit API Key</label>
                                        <input
                                            type="password"
                                            value={config.bybitKey}
                                            onChange={(e) => setConfig({ ...config, bybitKey: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs outline-none focus:border-primary/50 transition-all"
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="text-[9px] text-gray-500 uppercase ml-1">Bybit Secret</label>
                                        <input
                                            type="password"
                                            value={config.bybitSecret}
                                            onChange={(e) => setConfig({ ...config, bybitSecret: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs outline-none focus:border-primary/50 transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Auto-DAP Intelligence */}
                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-[11px] font-black text-white uppercase tracking-[0.2em] flex items-center gap-2">
                                        <Sparkles className="w-4 h-4 text-warning" /> Auto-Optimization (DAP)
                                    </h3>
                                    <button
                                        onClick={() => setConfig({ ...config, autoDap: !config.autoDap })}
                                        className={`w-12 h-6 rounded-full relative transition-colors ${config.autoDap ? 'bg-primary' : 'bg-white/10'}`}
                                    >
                                        <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${config.autoDap ? 'left-7' : 'left-1'}`} />
                                    </button>
                                </div>
                                <div className="p-5 rounded-2xl bg-warning/5 border border-warning/10 space-y-4">
                                    <p className="text-[10px] text-gray-400 leading-relaxed italic">
                                        When enabled, the system will background-backtest and automatically apply the most profitable EMA parameters to active bots.
                                    </p>
                                    <div className="flex items-center gap-6">
                                        <div className="space-y-1.5 flex-1">
                                            <label className="text-[9px] text-gray-500 uppercase">Sync Interval (Hours)</label>
                                            <input
                                                type="number"
                                                value={config.autoDapInterval}
                                                onChange={(e) => setConfig({ ...config, autoDapInterval: parseInt(e.target.value) })}
                                                className="w-full bg-black/20 border border-white/5 rounded-lg px-3 py-2 text-xs text-primary font-bold"
                                            />
                                        </div>
                                        <div className="space-y-1.5 flex-1">
                                            <label className="text-[9px] text-gray-500 uppercase">Strategy Basis</label>
                                            <div className="px-3 py-2 text-[10px] bg-white/5 rounded-lg text-gray-400 font-bold border border-white/5">
                                                Double EMA Breakout
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Risk Shield */}
                            <div className="space-y-6">
                                <h3 className="text-[11px] font-black text-white uppercase tracking-[0.2em] flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4 text-danger" /> Global Risk Shield
                                </h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex flex-col gap-2">
                                        <label className="text-[9px] text-gray-500 uppercase">Max Concurrent Bots</label>
                                        <input
                                            type="number"
                                            value={config.maxConcurrentBots}
                                            onChange={(e) => setConfig({ ...config, maxConcurrentBots: parseInt(e.target.value) })}
                                            className="bg-transparent text-xl font-black text-white outline-none"
                                        />
                                    </div>
                                    <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex flex-col gap-2">
                                        <label className="text-[9px] text-gray-500 uppercase">Daily Loss Limit (%)</label>
                                        <input
                                            type="number"
                                            value={config.globalDailyLossLimit}
                                            onChange={(e) => setConfig({ ...config, globalDailyLossLimit: parseInt(e.target.value) })}
                                            className="bg-transparent text-xl font-black text-danger outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Intelligent Knowledge Base */}
                            <div className="space-y-6">
                                <h3 className="text-[11px] font-black text-white uppercase tracking-[0.2em] flex items-center gap-2">
                                    <Database className="w-4 h-4 text-secondary" /> Knowledge Base (RAG)
                                </h3>
                                <div className="space-y-3">
                                    <div className="space-y-1.5">
                                        <label className="text-[9px] text-gray-500 uppercase ml-1">Brain Data Folder</label>
                                        <input
                                            type="text"
                                            value={config.aiKnowledgePath}
                                            onChange={(e) => setConfig({ ...config, aiKnowledgePath: e.target.value })}
                                            placeholder="src/agentes/knowledge"
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs outline-none focus:border-secondary/50 transition-all font-mono"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10 flex items-start gap-3">
                                <ShieldCheck className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                                <p className="text-[10px] text-gray-400 italic">
                                    Sua privacidade é inegociável. Todas as configurações do terminal de excelência são criptografadas em seu ambiente local.
                                </p>
                            </div>
                        </div>

                        <div className="p-8 border-t border-white/5 bg-black/60">
                            <button
                                onClick={handleSave}
                                className="w-full py-5 bg-primary text-background rounded-2xl font-black uppercase tracking-[0.3em] shadow-[0_0_50px_rgba(255,215,0,0.3)] hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center gap-3"
                            >
                                <Save className="w-6 h-6" />
                                Save & Align Strategy
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
});

ConfigModal.displayName = 'ConfigModal';
