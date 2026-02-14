import { memo } from 'react';
import { motion } from 'framer-motion';
import { Waves, ArrowUp, ArrowDown } from 'lucide-react';

export const LiquidationRadar = memo(() => {
    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="absolute top-1/2 right-4 -translate-y-1/2 z-10 flex flex-col items-center gap-2"
        >
            <div className="flex flex-col items-center gap-1 group">
                <div className="p-1.5 bg-yellow-500/20 rounded-lg cursor-pointer hover:bg-yellow-500/30 transition-all border border-yellow-500/10">
                    <Waves className="w-4 h-4 text-yellow-500" />
                </div>
                <div className="w-1.5 h-60 bg-black/40 rounded-full relative overflow-hidden border border-white/5 backdrop-blur-sm">
                    {/* Short Liquidations (Above Price) */}
                    <div className="absolute top-0 w-full h-[40%] bg-gradient-to-b from-red-500/80 via-red-500/20 to-transparent" />

                    {/* Long Liquidations (Below Price) */}
                    <div className="absolute bottom-0 w-full h-[40%] bg-gradient-to-t from-green-500/80 via-green-500/20 to-transparent" />

                    {/* Current Price Marker */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2.5 h-0.5 bg-white shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
                </div>
            </div>

            {/* Floating Labels (Simulated) */}
            <div className="absolute -left-[100px] top-4 px-2 py-1 bg-red-500/10 border border-red-500/20 rounded-md text-[9px] text-red-400 font-bold backdrop-blur-md flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <ArrowUp className="w-2.5 h-2.5" /> High Lev Stops
            </div>

            <div className="absolute -left-[100px] bottom-4 px-2 py-1 bg-green-500/10 border border-green-500/20 rounded-md text-[9px] text-green-400 font-bold backdrop-blur-md flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <ArrowDown className="w-2.5 h-2.5" /> Long Stops
            </div>
        </motion.div>
    );
});

LiquidationRadar.displayName = 'LiquidationRadar';
