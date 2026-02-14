import { memo } from 'react';
import { Search, Zap, Settings, Wifi, WifiOff, Globe } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useLanguage } from '../contexts/LanguageContext';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface HeaderProps {
    search: string;
    setSearch: (val: string) => void;
    isConnected: boolean;
    isConfiguring: boolean;
    setIsConfiguring: (val: boolean) => void;
    scanLimit: number;
    updateLimit: (limit: number) => void;
    userName: string;
    theme: string;
    setTheme: (theme: string) => void;
    openGlobalConfig: () => void;
    terminalMode: 'essential' | 'technical';
    onTerminalModeChange: (mode: 'essential' | 'technical') => void;
    wallet?: { balance: number; equity: number };
}

export const Header = memo(({
    search,
    setSearch,
    isConnected,
    isConfiguring,
    setIsConfiguring,
    scanLimit,
    updateLimit,
    userName,
    theme,
    setTheme,
    openGlobalConfig,
    onTerminalModeChange,
    terminalMode,
    wallet
}: HeaderProps) => {
    const { t, language, setLanguage } = useLanguage();
    const themes = [
        { id: 'gold', color: 'bg-[#ffd700]', label: 'Gold' },
        { id: 'cyber', color: 'bg-[#00e5ff]', label: 'Cyber' },
        { id: 'matrix', color: 'bg-[#00ff41]', label: 'Matrix' },
        { id: 'ruby', color: 'bg-[#ff1f1f]', label: 'Ruby' },
        { id: 'white', color: 'bg-[#ffffff]', label: 'Light' },
    ];
    return (
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 glass sticky top-0 z-50">
            <div className="flex items-center gap-3">
                <div className="p-2.5 bg-primary rounded-xl shadow-[0_0_20px_rgba(255,215,0,0.3)] border border-white/10">
                    <Zap className="w-6 h-6 text-background fill-current" />
                </div>
                <h1 className="font-black text-xl tracking-tighter leading-none flex items-center gap-2">
                    MONITOR <span className="text-primary">REINKE</span>
                </h1>

                {/* Wallet Info */}
                {wallet && (
                    <div className="hidden lg:flex flex-col ml-6 pl-6 border-l border-white/10">
                        <div className="flex items-center gap-4">
                            <div>
                                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">{t.header.balance}</span>
                                <span className="text-sm font-mono font-bold text-white">${wallet.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
                            </div>
                            <div>
                                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">{t.header.equity}</span>
                                <span className={clsx("text-sm font-mono font-bold", wallet.equity >= wallet.balance ? "text-green-400" : "text-red-400")}>
                                    ${wallet.equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="flex items-center gap-6">
                <div className="flex items-center gap-2 bg-white/5 px-4 py-2 rounded-full border border-white/5">
                    <Search className="w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder={t.header.filter}
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="bg-transparent border-none outline-none text-sm w-48 placeholder:text-gray-500"
                    />
                </div>

                {/* Theme Switcher */}
                <div className="flex items-center gap-1.5 p-1.5 bg-white/5 rounded-xl border border-white/10">
                    {themes.map((t) => (
                        <button
                            key={t.id}
                            onClick={() => setTheme(t.id)}
                            className={cn(
                                "w-4 h-4 rounded-full transition-all border",
                                theme === t.id ? "border-white scale-125 shadow-lg" : "border-transparent opacity-30 hover:opacity-100"
                            )}
                            title={t.label}
                        >
                            <div className={cn("w-full h-full rounded-full", t.color)} />
                        </button>
                    ))}
                </div>

                <div className="h-6 w-[1px] bg-white/10" />

                <div className="flex items-center gap-1 p-1 bg-white/5 rounded-xl border border-white/10">
                    <button
                        onClick={() => onTerminalModeChange('essential')}
                        className={cn(
                            "px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all",
                            terminalMode === 'essential'
                                ? "bg-primary text-background shadow-lg shadow-primary/20"
                                : "text-gray-500 hover:text-white"
                        )}
                    >
                        {t.header.essential}
                    </button>
                    <button
                        onClick={() => onTerminalModeChange('technical')}
                        className={cn(
                            "px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all",
                            terminalMode === 'technical'
                                ? "bg-primary text-background shadow-lg shadow-primary/20"
                                : "text-gray-500 hover:text-white"
                        )}
                    >
                        {t.header.technical}
                    </button>
                </div>

                <div className={cn(
                    "flex items-center gap-2 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider border",
                    isConnected ? "bg-success/10 text-success border-success/20" : "bg-danger/10 text-danger border-danger/20"
                )}>
                    {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                    {isConnected ? t.header.apiLive : t.header.offline}
                </div>

                <div className="flex items-center gap-2 relative">
                    <button
                        onClick={() => setIsConfiguring(!isConfiguring)}
                        className={cn("p-2 rounded-lg transition-colors shadow-lg", isConfiguring ? "bg-primary text-background" : "hover:bg-white/5")}
                    >
                        <Settings className="w-5 h-5" />
                    </button>

                    {isConfiguring && (
                        <div className="absolute top-12 right-0 w-64 glass p-4 rounded-xl z-[100] border-primary/20 shadow-2xl">
                            <h3 className="text-xs font-bold uppercase text-primary mb-3">{t.header.configTitle}</h3>
                            <p className="text-[10px] text-gray-400 mb-4 leading-tight">{t.header.configDesc}</p>
                            <input
                                type="range" min="1" max="160" value={scanLimit}
                                onChange={(e) => updateLimit(parseInt(e.target.value))}
                                className="w-full accent-primary mb-2"
                            />
                            <div className="flex justify-between text-[10px] font-mono text-primary mb-6">
                                <span>1</span>
                                <span className="font-bold text-sm italic">{scanLimit} {t.header.symbols}</span>
                                <span>160</span>
                            </div>

                            <button
                                onClick={() => {
                                    setIsConfiguring(false);
                                    openGlobalConfig();
                                }}
                                className="w-full py-3 bg-secondary/10 hover:bg-secondary/20 text-secondary rounded-xl text-[10px] font-black uppercase tracking-widest border border-secondary/20 transition-all flex items-center justify-center gap-2 shadow-lg"
                            >
                                <Globe className="w-4 h-4" /> {t.header.globalSettings}
                            </button>
                        </div>
                    )}
                </div>

                {/* Language Selector */}
                <div className="flex items-center gap-1 p-1 bg-white/5 rounded-xl border border-white/10 mr-2">
                    {(['pt', 'en', 'es'] as const).map((lang) => (
                        <button
                            key={lang}
                            onClick={() => setLanguage(lang)}
                            className={cn(
                                "px-2 py-1 rounded-lg text-[10px] font-bold uppercase transition-all",
                                language === lang
                                    ? "bg-primary text-background shadow-lg"
                                    : "text-gray-500 hover:text-white"
                            )}
                        >
                            {lang}
                        </button>
                    ))}
                </div>

                <div className="h-4 w-[1px] bg-white/10" />
                <div className="flex items-center gap-2 text-primary">
                    <span className="text-xs font-bold uppercase tracking-widest">{userName}</span>
                </div>
            </div>
        </header>
    );
});

Header.displayName = 'Header';
