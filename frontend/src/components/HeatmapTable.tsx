import { memo } from 'react';
import { ArrowUp, ArrowDown, ExternalLink, Zap, Plus, Star } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useScanner } from '../hooks/useMarketData';
import { useLanguage } from '../contexts/LanguageContext';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

interface HeatmapTableProps {
    setSelectedSymbol: (symbol: string) => void;
    onOpenTicket: (symbol: string, price: number) => void;
    scanLimit: number;
    terminalMode: 'essential' | 'technical';
}

export const HeatmapTable = memo(({ setSelectedSymbol, onOpenTicket, terminalMode }: HeatmapTableProps) => {
    const { t } = useLanguage();
    const { data: scannerData } = useScanner();
    const isTechnical = terminalMode === 'technical';

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="text-[10px] uppercase text-gray-500 border-b border-white/10">
                        <th className="px-6 py-3 font-bold tracking-wider">{t.table.asset}</th>
                        <th className="px-6 py-3 font-bold tracking-wider text-center">{t.table.score}</th>
                        {isTechnical && <th className="px-6 py-3 font-bold tracking-wider text-center">{t.table.rsi}</th>}
                        {isTechnical && <th className="px-6 py-3 font-bold tracking-wider text-center">{t.table.factors}</th>}
                        <th className="px-2 py-3"></th>
                        <th className="px-6 py-3 font-bold tracking-wider text-right">{t.table.price}</th>
                        <th className="px-6 py-3 font-bold tracking-wider text-right">{t.table.action}</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    {scannerData.map((item) => (
                        <tr key={item.symbol} className="hover:bg-white/[0.03] transition-colors group">
                            {/* Symbol / Score Badge */}
                            <td className="px-6 py-5">
                                <div className="flex items-center gap-3">
                                    <div className={cn(
                                        "w-8 h-8 rounded-full bg-white/5 flex items-center justify-center font-bold text-xs border border-white/10 uppercase",
                                        item.score >= 4 && "border-primary/50 text-primary shadow-[0_0_10px_rgba(255,215,0,0.2)]"
                                    )}>
                                        {item.symbol.substring(0, 1)}
                                    </div>
                                    <span className="font-bold text-sm tracking-tight">{item.symbol}</span>
                                </div>
                            </td>

                            {/* AI Score Stars */}
                            <td className="px-6 py-4">
                                <div className="flex justify-center gap-0.5">
                                    {[...Array(5)].map((_, j) => (
                                        <Star
                                            key={j}
                                            className={cn(
                                                "w-3 h-3",
                                                j < item.score ? "text-primary fill-primary drop-shadow-[0_0_5px_rgba(255,215,0,0.6)]" : "text-white/10"
                                            )}
                                        />
                                    ))}
                                </div>
                            </td>

                            {/* Technical Columns */}
                            {isTechnical && (
                                <td className="px-6 py-4 text-center">
                                    <span className={cn(
                                        "text-xs font-mono font-bold",
                                        item.rsi > 70 ? "text-danger" : item.rsi < 30 ? "text-success" : "text-primary/70"
                                    )}>
                                        {item.rsi}
                                    </span>
                                </td>
                            )}
                            {isTechnical && (
                                <td className="px-6 py-4">
                                    <div className="flex gap-2 justify-center translate-y-0.5">
                                        {Object.entries(item.factors).map(([key, val], idx) => (
                                            <div
                                                key={idx}
                                                title={key}
                                                className={cn(
                                                    "w-2.5 h-2.5 rounded-sm",
                                                    val ? "bg-success shadow-[0_0_5px_rgba(0,200,83,0.5)]" : "bg-white/5 border border-white/5"
                                                )}
                                            />
                                        ))}
                                    </div>
                                </td>
                            )}

                            {/* Ticket Button */}
                            <td className="p-2 text-right">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onOpenTicket(item.symbol, item.price);
                                    }}
                                    className="p-1 hover:bg-white/10 rounded text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                    title="Open Trade Ticket"
                                >
                                    <Zap className="w-4 h-4 text-yellow-400 fill-current" />
                                </button>
                            </td>

                            {/* Price */}
                            <td className="px-6 py-4 text-right">
                                <span className="font-mono text-xs text-secondary group-hover:text-primary transition-colors">
                                    ${item.price.toLocaleString()}
                                </span>
                            </td>

                            {/* Deploy Button */}
                            <td className="px-6 py-4 text-right">
                                <button
                                    onClick={() => setSelectedSymbol(item.symbol)}
                                    className="bg-primary/10 hover:bg-primary text-primary hover:text-background p-1.5 rounded-lg border border-primary/20 transition-all group-hover:scale-110"
                                    title="Open Chart"
                                >
                                    <Plus className="w-4 h-4" />
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
});

HeatmapTable.displayName = 'HeatmapTable';
