import { memo } from 'react';
import { TrendingUp, TrendingDown, History, BarChart2, Target, AlertCircle } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { PerformanceStats, TradeHistoryItem } from '../types';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface PerformancePanelProps {
    stats: PerformanceStats;
    history: TradeHistoryItem[];
}

export const PerformancePanel = memo(({ stats, history }: PerformancePanelProps) => {
    return (
        <div className="flex flex-col gap-6 h-full overflow-hidden p-1">
            {/* Quick Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
                <div className="glass p-3 rounded-xl border-white/5 bg-white/[0.02]">
                    <div className="flex items-center gap-2 text-primary mb-1">
                        <BarChart2 className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Total PnL</span>
                    </div>
                    <p className={cn(
                        "text-lg font-bold font-mono",
                        stats.totalPnL >= 0 ? "text-success" : "text-danger"
                    )}>
                        {stats.totalPnL >= 0 ? '+' : ''}{stats.totalPnL.toFixed(2)} USDT
                    </p>
                </div>

                <div className="glass p-3 rounded-xl border-white/5 bg-white/[0.02]">
                    <div className="flex items-center gap-2 text-secondary mb-1">
                        <Target className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Win Rate</span>
                    </div>
                    <p className="text-lg font-bold font-mono text-secondary">
                        {stats.winRate.toFixed(1)}%
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 p-2.5 rounded-lg border border-white/5 flex flex-col items-center">
                    <span className="text-[9px] text-gray-500 uppercase tracking-tighter">Total Trades</span>
                    <span className="text-sm font-bold">{stats.totalTrades}</span>
                </div>
                <div className="bg-white/5 p-2.5 rounded-lg border border-white/5 flex flex-col items-center">
                    <span className="text-[9px] text-gray-500 uppercase tracking-tighter">Profit Factor</span>
                    <span className="text-sm font-bold">{stats.profitFactor.toFixed(2)}</span>
                </div>
            </div>

            {/* Trade History */}
            <div className="flex-1 flex flex-col overflow-hidden min-h-0">
                <div className="flex items-center gap-2 text-gray-400 mb-3 px-1">
                    <History className="w-4 h-4 text-primary" />
                    <h3 className="text-[10px] font-bold uppercase tracking-widest">Trade History</h3>
                </div>

                <div className="flex-1 overflow-auto space-y-2 pr-2 custom-scrollbar">
                    {history.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-40 border border-dashed border-white/10 rounded-2xl opacity-40">
                            <AlertCircle className="w-8 h-8 mb-2" />
                            <p className="text-[11px] italic">No closed trades recorded yet.</p>
                        </div>
                    ) : history.map((trade, i) => (
                        <div key={i} className="glass p-3 rounded-xl border-white/5 flex items-center justify-between hover:bg-white/[0.04] transition-colors">
                            <div className="flex items-center gap-3">
                                <div className={cn(
                                    "p-2 rounded-lg",
                                    trade.pnl >= 0 ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
                                )}>
                                    {trade.side === 'compra' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                                </div>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-xs">{trade.symbol}</span>
                                        <span className={cn(
                                            "text-[9px] px-1.5 py-0.5 rounded-sm uppercase font-bold",
                                            trade.result === 'target' ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'
                                        )}>
                                            {trade.result}
                                        </span>
                                    </div>
                                    <p className="text-[9px] text-gray-500 uppercase tracking-tighter">
                                        {new Date(trade.closed_at).toLocaleDateString()} • {new Date(trade.closed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className={cn(
                                    "font-bold text-xs font-mono",
                                    trade.pnl >= 0 ? "text-success" : "text-danger"
                                )}>
                                    {trade.pnl >= 0 ? '+' : ''}{trade.pnl.toFixed(2)}
                                </p>
                                <p className="text-[9px] text-gray-500 font-mono">
                                    {trade.pnl_percent.toFixed(2)}%
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
});

PerformancePanel.displayName = 'PerformancePanel';
