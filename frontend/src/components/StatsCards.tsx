import { memo } from 'react';
import { Layers, Zap, Activity, ShieldCheck } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { BotSummary, ScannerResult } from '../types';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface StatsCardsProps {
    scannerData: ScannerResult[];
    bots: BotSummary[];
    isConnected: boolean;
    totalExposedRisk?: number;
}

export const StatsCards = memo(({ scannerData, bots, totalExposedRisk = 0 }: StatsCardsProps) => {
    const stats = [
        { label: 'Market Scope', value: scannerData.length, icon: Layers, color: 'text-secondary' },
        { label: 'Hot Targets', value: scannerData.filter(s => s.score === 5).length, icon: Zap, color: 'text-primary' },
        { label: 'Running Bots', value: bots.filter(b => b.status === 'running').length, icon: Activity, color: 'text-success' },
        { label: 'Risk Exposure', value: `${totalExposedRisk.toFixed(1)}%`, icon: ShieldCheck, color: totalExposedRisk > 5 ? 'text-danger' : 'text-success' },
    ];

    return (
        <div className="grid grid-cols-4 gap-4">
            {stats.map((stat, i) => (
                <div key={i} className="glass rounded-xl p-4 flex items-center gap-4 hover:border-white/10 transition-all cursor-default">
                    <div className={cn("p-2 rounded-lg bg-white/5", stat.color)}>
                        <stat.icon className="w-5 h-5" />
                    </div>
                    <div>
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">{stat.label}</p>
                        <p className="text-xl font-bold">{stat.value}</p>
                    </div>
                </div>
            ))}
        </div>
    );
});

StatsCards.displayName = 'StatsCards';
