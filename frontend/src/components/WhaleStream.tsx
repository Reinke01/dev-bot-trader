import { useState, useEffect, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Fish, ChevronDown } from 'lucide-react';
import { clsx } from 'clsx';

interface WhaleTrade {
    id: string;
    symbol: string;
    side: 'buy' | 'sell';
    amount: number;
    price: number;
    timestamp: number;
}

const formatMoney = (val: number) => {
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
    return `$${(val / 1000).toFixed(0)}k`;
};

export const WhaleStream = memo(({ symbol }: { symbol: string }) => {
    const [trades, setTrades] = useState<WhaleTrade[]>([]);
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Simulate Whale Data Stream
    useEffect(() => {
        const generateTrade = (): WhaleTrade => {
            const side = Math.random() > 0.45 ? 'buy' : 'sell'; // Slight buy bias
            const amount = 50000 + Math.random() * 2000000;
            return {
                id: Math.random().toString(36).substr(2, 9),
                symbol,
                side: side as 'buy' | 'sell',
                amount,
                price: 0, // Placeholder
                timestamp: Date.now()
            };
        };

        // Initial population
        setTrades(Array(3).fill(null).map(generateTrade));

        const interval = setInterval(() => {
            if (Math.random() > 0.3) { // 70% chance to add trade
                const newTrade = generateTrade();
                setTrades(prev => [newTrade, ...prev].slice(0, 5));
            }
        }, 3000);

        return () => clearInterval(interval);
    }, [symbol]);

    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-4 left-4 z-10 flex flex-col items-start gap-2"
        >
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="flex items-center gap-2 px-3 py-1.5 glass rounded-full border border-white/10 hover:bg-white/10 transition-all group"
            >
                <div className="p-1 bg-purple-500/20 rounded-full">
                    <Fish className="w-3 h-3 text-purple-400" />
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest text-purple-200">Whale Stream</span>
                <ChevronDown className={clsx("w-3 h-3 text-white/50 transition-transform", isCollapsed && "rotate-180")} />
            </button>

            <AnimatePresence>
                {!isCollapsed && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="flex flex-col gap-1 w-[220px]"
                    >
                        {trades.map((trade) => (
                            <motion.div
                                key={trade.id}
                                layout
                                initial={{ opacity: 0, x: -20, scale: 0.9 }}
                                animate={{ opacity: 1, x: 0, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.5 }}
                                className={clsx(
                                    "flex items-center justify-between p-2 rounded-xl backdrop-blur-md border shadow-lg",
                                    trade.side === 'buy'
                                        ? "bg-success/10 border-success/20 shadow-success/5"
                                        : "bg-danger/10 border-danger/20 shadow-danger/5"
                                )}
                            >
                                <div className="flex items-center gap-2">
                                    <span className={clsx(
                                        "text-[9px] font-black uppercase px-1.5 py-0.5 rounded",
                                        trade.side === 'buy' ? "bg-success/20 text-success" : "bg-danger/20 text-danger"
                                    )}>
                                        {trade.side}
                                    </span>
                                    <span className="text-[10px] font-bold text-white/90">
                                        {formatMoney(trade.amount)}
                                    </span>
                                </div>
                                <span className="text-[9px] text-white/40 font-mono">
                                    {new Date(trade.timestamp).toLocaleTimeString([], { hour12: false, minute: '2-digit', second: '2-digit' })}
                                </span>
                            </motion.div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
});
WhaleStream.displayName = 'WhaleStream';
