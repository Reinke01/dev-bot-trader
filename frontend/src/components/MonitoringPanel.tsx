import { memo } from 'react';
import { Terminal, Activity, Cpu, Trash2, BarChart2, FlaskConical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { LogEntry, BotSummary, PerformanceStats, TradeHistoryItem } from '../types';
import { PerformancePanel } from './PerformancePanel';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface MonitoringPanelProps {
    activeTab: 'terminal' | 'bots' | 'performance';
    setActiveTab: (tab: 'terminal' | 'bots' | 'performance') => void;
    logs: LogEntry[];
    bots: BotSummary[];
    performanceStats: PerformanceStats;
    tradeHistory: TradeHistoryItem[];
    stopBot: (botId: string) => void;
}

export const MonitoringPanel = memo(({
    activeTab,
    setActiveTab,
    logs,
    bots,
    performanceStats,
    tradeHistory,
    stopBot
}: MonitoringPanelProps) => {
    return (
        <div className="glass rounded-2xl flex-1 flex flex-col overflow-hidden bg-black/20">
            <div className="p-6 border-b border-white/5 flex items-center justify-between ">
                <div className="flex gap-4">
                    <button
                        onClick={() => setActiveTab('terminal')}
                        className={cn(
                            "font-bold flex items-center gap-2 transition-colors",
                            activeTab === 'terminal' ? "text-secondary" : "text-gray-500 hover:text-gray-300"
                        )}
                    >
                        <Terminal className="w-4 h-4" />
                        Terminal
                    </button>
                    <button
                        onClick={() => setActiveTab('bots')}
                        className={cn(
                            "font-bold flex items-center gap-2 transition-colors",
                            activeTab === 'bots' ? "text-primary" : "text-gray-500 hover:text-gray-300"
                        )}
                    >
                        <Activity className="w-4 h-4" />
                        Active Bots
                        {bots.length > 0 && (
                            <span className="bg-primary/20 text-primary text-[10px] px-1.5 py-0.5 rounded-full ml-1">
                                {bots.length}
                            </span>
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('performance')}
                        className={cn(
                            "font-bold flex items-center gap-2 transition-colors",
                            activeTab === 'performance' ? "text-primary" : "text-gray-500 hover:text-gray-300"
                        )}
                    >
                        <BarChart2 className="w-4 h-4" />
                        PnL
                    </button>
                </div>
                <div className="flex items-center gap-1.5 bg-success/10 px-2 py-0.5 rounded border border-success/20">
                    <span className="text-[10px] text-success font-bold font-mono">
                        {activeTab === 'terminal' ? 'STREAMING' : activeTab === 'bots' ? 'LIVE MONITOR' : 'RESULTS'}
                    </span>
                </div>
            </div>

            <div className="flex-1 bg-[#050507] p-4 font-mono text-[10px] overflow-auto">
                <AnimatePresence mode="wait">
                    {activeTab === 'terminal' ? (
                        <motion.div
                            key="terminal"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="flex flex-col-reverse gap-2 h-full"
                        >
                            {logs.length === 0 ? (
                                <div className="text-gray-700 italic">Listening for system events (Throttled 2fps)...</div>
                            ) : logs.map((log, i) => (
                                <div key={i} className="flex gap-2 border-l border-white/5 pl-2 animate-in fade-in slide-in-from-left-1 duration-300">
                                    <span className="text-gray-600 shrink-0">[{log.timestamp?.split('T')[1]?.split('.')[0] || '--:--'}]</span>
                                    <span className={cn(
                                        "font-bold shrink-0",
                                        log.level === 'TRADING' ? 'text-success' : 'text-secondary'
                                    )}>
                                        {log.level}:
                                    </span>
                                    <span className="text-gray-400 truncate">{log.message}</span>
                                </div>
                            ))}
                        </motion.div>
                    ) : activeTab === 'bots' ? (
                        <motion.div
                            key="bots"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="flex flex-col gap-3 h-full"
                        >
                            {bots.length === 0 ? (
                                <div className="text-gray-700 italic text-center mt-10">No active bots found. Deploy one from the Heatmap.</div>
                            ) : bots.map((bot, i) => (
                                <div key={i} className="glass p-3 rounded-xl border-white/5 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-primary/10 text-primary">
                                            <Cpu className="w-4 h-4" />
                                        </div>
                                        <div>
                                            <p className="font-bold text-xs uppercase">{bot.cripto}</p>
                                            <p className="text-[9px] text-gray-500 uppercase tracking-tighter">
                                                TF: {bot.tempo_grafico}m • ID: {bot.bot_id.split('-')[0]}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        {bot.is_simulator && (
                                            <div className="px-2 py-0.5 rounded-full bg-warning/10 text-warning text-[9px] font-bold uppercase border border-warning/20 flex items-center gap-1">
                                                <FlaskConical className="w-2 h-2" />
                                                Simulated
                                            </div>
                                        )}
                                        <div className={cn(
                                            "px-2 py-0.5 rounded-full text-[9px] font-bold uppercase",
                                            bot.status === 'running' ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
                                        )}>
                                            {bot.status}
                                        </div>
                                        <button
                                            onClick={() => stopBot(bot.bot_id)}
                                            className="p-1.5 rounded-md hover:bg-danger/20 text-gray-500 hover:text-danger transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </motion.div>
                    ) : (
                        <motion.div
                            key="performance"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="h-full"
                        >
                            <PerformancePanel stats={performanceStats} history={tradeHistory} />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
});

MonitoringPanel.displayName = 'MonitoringPanel';
