import { useState, memo } from 'react';
import { LayoutDashboard, History, TrendingUp, Bot, ExternalLink, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import type { BotSummary, TradeHistoryItem, PerformanceStats } from '../types';

interface TradeManagementProps {
    bots: BotSummary[];
    history: TradeHistoryItem[];
    stats: PerformanceStats;
    stopBot: (id: string) => void;
    terminalMode: 'essential' | 'technical';
}

export const TradeManagement = memo(({ bots, history, stats, stopBot, terminalMode }: TradeManagementProps) => {
    const [activeTab, setActiveTab] = useState<'active' | 'history' | 'stats'>('active');
    const isTechnical = terminalMode === 'technical';

    // Filter out system services (like Scanner, SignalService) that don't have a crypto symbol
    const activeTradingBots = bots.filter(b => b.cripto !== null && b.cripto !== undefined);

    return (
        <div className="glass rounded-3xl overflow-hidden flex flex-col h-full border border-white/5">
            {/* Tab Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/5 bg-white/[0.01]">
                <div className="flex gap-1 p-1 bg-black/20 rounded-2xl border border-white/5">
                    {[
                        { id: 'active', label: `Active (${activeTradingBots.length})`, icon: Bot },
                        { id: 'history', label: 'History', icon: History },
                        { id: 'stats', label: 'Stats', icon: TrendingUp },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all",
                                activeTab === tab.id ? "bg-primary text-background shadow-lg" : "text-gray-500 hover:text-white"
                            )}
                        >
                            <tab.icon className="w-3.5 h-3.5" />
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className="flex items-center gap-4 px-4">
                    <div className="text-right">
                        <p className="text-[9px] text-gray-500 font-bold uppercase tracking-widest">Total PnL</p>
                        <p className={clsx(
                            "text-sm font-black font-mono",
                            stats.totalPnL >= 0 ? "text-success" : "text-danger"
                        )}>
                            {stats.totalPnL >= 0 ? '+' : ''}{stats.totalPnL.toFixed(2)} USDT
                        </p>
                    </div>
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-auto custom-scrollbar p-6">
                <AnimatePresence mode="wait">
                    {activeTab === 'active' && (
                        <motion.div
                            key="active"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="space-y-4"
                        >
                            {activeTradingBots.length === 0 ? (
                                <div className="py-20 text-center opacity-30 italic text-sm">No active bots running</div>
                            ) : (
                                <div className="grid grid-cols-1 gap-3">
                                    {activeTradingBots.map((bot) => (
                                        <div key={bot.bot_id} className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-primary/30 transition-all flex items-center justify-between group">
                                            <div className="flex items-center gap-4">
                                                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
                                                    <span className="text-primary font-black text-xs">{bot.cripto.substring(0, 1)}</span>
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-bold text-sm">{bot.cripto}</span>
                                                        {bot.is_simulator && (
                                                            <span className="text-[8px] px-1.5 py-0.5 bg-warning/20 text-warning rounded-md font-black uppercase tracking-tighter">SIM</span>
                                                        )}
                                                    </div>
                                                    <p className="text-[10px] text-gray-500 font-mono">ID: {bot.bot_id.substring(0, 8)}</p>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-8">
                                                {isTechnical && (
                                                    <div className="text-right">
                                                        <p className="text-[9px] text-gray-500 uppercase font-black">EMA Strategy</p>
                                                        <p className="text-[10px] font-mono">{bot.ema_rapida_compra}/{bot.ema_lenta_compra}</p>
                                                    </div>
                                                )}
                                                <div className="text-right">
                                                    <p className="text-[9px] text-gray-500 uppercase font-black">Status</p>
                                                    <span className="text-[10px] text-success font-bold uppercase animate-pulse">{bot.status}</span>
                                                </div>
                                                <button
                                                    onClick={() => stopBot(bot.bot_id)}
                                                    className="p-2 bg-danger/10 hover:bg-danger text-danger hover:text-white rounded-lg transition-all"
                                                >
                                                    <ArrowDownRight className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    )}

                    {activeTab === 'history' && (
                        <motion.div
                            key="history"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                        >
                            <table className="w-full text-left">
                                <thead className="text-[9px] text-gray-500 uppercase tracking-widest border-b border-white/5">
                                    <tr>
                                        <th className="pb-3 px-2">Symbol</th>
                                        <th className="pb-3 px-2">Side</th>
                                        <th className="pb-3 px-2">Result</th>
                                        <th className="pb-3 px-2 text-right">PnL</th>
                                        <th className="pb-3 px-2 text-right">Time</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/[0.02]">
                                    {history.map((trade, i) => (
                                        <tr key={i} className="group hover:bg-white/[0.01]">
                                            <td className="py-3 px-2 text-xs font-bold">{trade.symbol}</td>
                                            <td className="py-3 px-2">
                                                <span className={clsx(
                                                    "text-[9px] font-black uppercase",
                                                    trade.side === 'compra' ? "text-success" : "text-danger"
                                                )}>
                                                    {trade.side}
                                                </span>
                                            </td>
                                            <td className="py-3 px-2">
                                                <span className={clsx(
                                                    "px-1.5 py-0.5 rounded text-[8px] font-black uppercase",
                                                    trade.result === 'target' ? "bg-success/20 text-success" : "bg-danger/20 text-danger"
                                                )}>
                                                    {trade.result}
                                                </span>
                                            </td>
                                            <td className={clsx(
                                                "py-3 px-2 text-right font-mono text-xs font-bold",
                                                trade.pnl >= 0 ? "text-success" : "text-danger"
                                            )}>
                                                {trade.pnl > 0 ? '+' : ''}{trade.pnl.toFixed(2)}
                                            </td>
                                            <td className="py-3 px-2 text-right text-[10px] text-gray-500 font-mono">
                                                {new Date(trade.closed_at).toLocaleTimeString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </motion.div>
                    )}

                    {activeTab === 'stats' && (
                        <motion.div
                            key="stats"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="grid grid-cols-2 gap-4"
                        >
                            <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/5 flex flex-col items-center justify-center text-center">
                                <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2">Win Rate</p>
                                <p className="text-4xl font-black text-primary">{stats.winRate.toFixed(1)}%</p>
                                <div className="w-full bg-white/5 h-1.5 rounded-full mt-4 overflow-hidden">
                                    <div className="bg-primary h-full" style={{ width: `${stats.winRate}%` }} />
                                </div>
                            </div>
                            <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/5 flex flex-col items-center justify-center text-center">
                                <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2">Profit Factor</p>
                                <p className="text-4xl font-black text-secondary">{stats.profitFactor.toFixed(2)}</p>
                                <p className="text-[9px] text-gray-500 mt-2 italic">Based on {stats.totalTrades} closed trades</p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
});

TradeManagement.displayName = 'TradeManagement';
