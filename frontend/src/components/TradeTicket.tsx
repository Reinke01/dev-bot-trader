
import { useState } from 'react';
import { clsx } from 'clsx';
import { useLanguage } from '../contexts/LanguageContext';
import { ArrowUpCircle, ArrowDownCircle, DollarSign, Percent, AlertCircle } from 'lucide-react';

interface TradeTicketProps {
    symbol: string;
    currentPrice: number;
    onClose: () => void;
}

export const TradeTicket = ({ symbol, currentPrice = 0, onClose }: TradeTicketProps) => {
    const { t } = useLanguage();
    const [side, setSide] = useState<'buy' | 'sell'>('buy');
    const [type, setType] = useState<'market' | 'limit'>('limit');
    const [price, setPrice] = useState<string>(currentPrice.toString());
    const [amount, setAmount] = useState<string>('');
    const [leverage, setLeverage] = useState<number>(1);

    const isBuy = side === 'buy';

    // Mock calculations
    const total = parseFloat(amount || '0') * (type === 'limit' ? parseFloat(price || '0') : currentPrice);

    return (
        <div className="flex flex-col h-full bg-[#0f1115] text-white">
            {/* Header / Tabs */}
            <div className="flex border-b border-white/10">
                <button
                    onClick={() => setSide('buy')}
                    className={clsx(
                        "flex-1 py-3 text-xs font-black uppercase tracking-widest transition-colors border-b-2",
                        side === 'buy'
                            ? "border-green-500 text-green-400 bg-green-500/5"
                            : "border-transparent text-gray-500 hover:text-white"
                    )}
                >
                    {t.ticket.buyLong}
                </button>
                <button
                    onClick={() => setSide('sell')}
                    className={clsx(
                        "flex-1 py-3 text-xs font-black uppercase tracking-widest transition-colors border-b-2",
                        side === 'sell'
                            ? "border-red-500 text-red-400 bg-red-500/5"
                            : "border-transparent text-gray-500 hover:text-white"
                    )}
                >
                    {t.ticket.sellShort}
                </button>
            </div>

            <div className="p-4 flex-1 overflow-y-auto">
                {/* Order Type */}
                <div className="flex bg-white/5 p-1 rounded-lg mb-4">
                    {['limit', 'market'].map((orderType) => (
                        <button
                            key={orderType}
                            onClick={() => setType(orderType as 'limit' | 'market')}
                            className={clsx(
                                "flex-1 py-1.5 rounded text-[10px] font-bold uppercase transition-all",
                                type === orderType
                                    ? "bg-white/10 text-white shadow-sm"
                                    : "text-gray-500 hover:text-white"
                            )}
                        >
                            {orderType === 'limit' ? t.ticket.typeLimit : t.ticket.typeMarket}
                        </button>
                    ))}
                </div>

                {/* Price Input */}
                {type === 'limit' && (
                    <div className="mb-4">
                        <label className="text-[10px] uppercase font-bold text-gray-500 mb-1.5 block">{t.ticket.price} (USDT)</label>
                        <div className="relative group">
                            <input
                                type="number"
                                value={price}
                                onChange={(e) => setPrice(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg py-2.5 px-3 text-sm font-mono focus:border-primary focus:outline-none transition-colors"
                            />
                            <span className="absolute right-3 top-2.5 text-xs text-gray-500">USDT</span>
                        </div>
                    </div>
                )}

                {/* Amount Input */}
                <div className="mb-6">
                    <label className="text-[10px] uppercase font-bold text-gray-500 mb-1.5 block">{t.ticket.amount} ({symbol.replace('USDT', '')})</label>
                    <div className="relative">
                        <input
                            type="number"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            placeholder="0.00"
                            className="w-full bg-white/5 border border-white/10 rounded-lg py-2.5 px-3 text-sm font-mono focus:border-primary focus:outline-none transition-colors"
                        />
                    </div>
                    {/* Percent Quick Select */}
                    <div className="flex gap-2 mt-2">
                        {[25, 50, 75, 100].map(pct => (
                            <button key={pct} className="flex-1 py-1 bg-white/5 hover:bg-white/10 rounded text-[10px] text-gray-400 font-mono transition-colors">
                                {pct}%
                            </button>
                        ))}
                    </div>
                </div>

                {/* Leverage Slider (Mock) */}
                <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-[10px] uppercase font-bold text-gray-500">{t.ticket.leverage}</label>
                        <span className="text-xs font-bold text-yellow-400">{leverage}x</span>
                    </div>
                    <input
                        type="range" min="1" max="100"
                        value={leverage} onChange={(e) => setLeverage(parseInt(e.target.value))}
                        className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-yellow-400"
                    />
                </div>

                {/* Summary */}
                <div className="bg-white/5 p-3 rounded-lg mb-6 space-y-2">
                    <div className="flex justify-between text-xs">
                        <span className="text-gray-500">{t.ticket.cost}</span>
                        <span className="font-mono text-white">{(total / leverage).toFixed(2)} USDT</span>
                    </div>
                    <div className="flex justify-between text-xs">
                        <span className="text-gray-500">{t.ticket.value}</span>
                        <span className="font-mono text-white">{total.toFixed(2)} USDT</span>
                    </div>
                </div>

                {/* Action Button */}
                <button
                    className={clsx(
                        "w-full py-4 rounded-xl font-black uppercase tracking-widest text-sm shadow-lg hover:brightness-110 active:scale-[0.98] transition-all flex items-center justify-center gap-2",
                        isBuy ? "bg-green-500 text-black shadow-green-500/20" : "bg-red-500 text-white shadow-red-500/20"
                    )}
                >
                    {isBuy ? <ArrowUpCircle className="w-5 h-5" /> : <ArrowDownCircle className="w-5 h-5" />}
                    {isBuy ? `${t.ticket.actionBuy} ${symbol.replace('USDT', '')}` : `${t.ticket.actionSell} ${symbol.replace('USDT', '')}`}
                </button>
            </div>
        </div>
    );
};
