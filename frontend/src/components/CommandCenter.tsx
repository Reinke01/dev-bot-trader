import { useState, useEffect, useRef, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Zap, Palette, CornerDownLeft, Bot, ExternalLink, Moon, Sun, X } from 'lucide-react';
import { clsx } from 'clsx';

interface CommandCenterProps {
    isOpen: boolean;
    onClose: () => void;
    onExecute: (command: string) => void;
    currentTheme: string;
}

export const CommandCenter = memo(({ isOpen, onClose, onExecute, currentTheme }: CommandCenterProps) => {
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);

    const commands = [
        { id: 'deploy', label: 'Deploy Bot', icon: Bot, description: 'Start a new trading bot for a symbol', shortcut: 'D' },
        { id: 'theme-toggle', label: `Switch to ${currentTheme === 'white' ? 'Dark' : 'Light'} Mode`, icon: currentTheme === 'white' ? Moon : Sun, description: 'Toggle between light and dark themes', shortcut: 'T' },
        { id: 'close-all', label: 'Panic: Stop All Bots', icon: X, description: 'Immediately stop all running bots', shortcut: 'X', danger: true },
        { id: 'goto-btc', label: 'View BTC/USDT', icon: Search, description: 'Switch chart and analysis to Bitcoin', shortcut: 'B' },
        { id: 'optimize', label: 'Run DAP Optimization', icon: Zap, description: 'Calculate best EMA parameters', shortcut: 'O' },
    ];

    const filtered = commands.filter(c =>
        c.label.toLowerCase().includes(query.toLowerCase()) ||
        c.id.toLowerCase().includes(query.toLowerCase())
    );

    useEffect(() => {
        if (isOpen) {
            setQuery('');
            setSelectedIndex(0);
            setTimeout(() => inputRef.current?.focus(), 10);
        }
    }, [isOpen]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setSelectedIndex(i => (i + 1) % filtered.length);
            }
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                setSelectedIndex(i => (i - 1 + filtered.length) % filtered.length);
            }
            if (e.key === 'Enter' && filtered[selectedIndex]) {
                onExecute(filtered[selectedIndex].id);
                onClose();
            }
        };

        if (isOpen) window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, filtered, selectedIndex, onClose, onExecute]);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-background/80 backdrop-blur-sm z-[200]"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -20 }}
                        className="fixed top-1/4 left-1/2 -translate-x-1/2 w-full max-w-xl glass rounded-3xl z-[201] border border-white/10 shadow-2xl overflow-hidden"
                    >
                        <div className="flex items-center gap-4 p-6 border-b border-white/5">
                            <Search className="w-5 h-5 text-primary animate-pulse" />
                            <input
                                ref={inputRef}
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Type a command or search..."
                                className="bg-transparent border-none outline-none text-lg w-full placeholder:text-gray-500 font-medium"
                            />
                            <div className="px-2 py-1 bg-white/5 rounded-lg text-[10px] font-bold text-gray-500 border border-white/5 uppercase">
                                ESC to close
                            </div>
                        </div>

                        <div className="max-h-[400px] overflow-y-auto custom-scrollbar p-2">
                            {filtered.length === 0 ? (
                                <div className="p-10 text-center opacity-30 italic">No results found</div>
                            ) : (
                                filtered.map((cmd, i) => (
                                    <button
                                        key={cmd.id}
                                        onClick={() => {
                                            onExecute(cmd.id);
                                            onClose();
                                        }}
                                        className={clsx(
                                            "w-full flex items-center justify-between p-4 rounded-2xl transition-all group",
                                            selectedIndex === i ? "bg-primary text-background" : "hover:bg-white/5"
                                        )}
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={clsx(
                                                "p-2.5 rounded-xl border",
                                                selectedIndex === i ? "bg-background/20 border-white/20" : "bg-white/5 border-white/10"
                                            )}>
                                                <cmd.icon className="w-4 h-4" />
                                            </div>
                                            <div className="text-left">
                                                <p className="text-sm font-bold tracking-tight">{cmd.label}</p>
                                                <p className={clsx(
                                                    "text-[10px] font-medium leading-tight",
                                                    selectedIndex === i ? "text-background/70" : "text-gray-500"
                                                )}>
                                                    {cmd.description}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            {cmd.danger && (
                                                <span className={clsx(
                                                    "text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded",
                                                    selectedIndex === i ? "bg-red-500 text-white" : "bg-red-500/20 text-red-500"
                                                )}>
                                                    Danger
                                                </span>
                                            )}
                                            <div className={clsx(
                                                "flex items-center gap-1.5 px-2 py-1 rounded-lg border",
                                                selectedIndex === i ? "bg-background/20 border-white/20" : "bg-white/5 border-white/10"
                                            )}>
                                                <CornerDownLeft className="w-3 h-3" />
                                                <span className="text-[10px] font-bold uppercase">{cmd.shortcut}</span>
                                            </div>
                                        </div>
                                    </button>
                                ))
                            )}
                        </div>

                        <div className="p-4 bg-black/20 border-t border-white/5 flex justify-between items-center">
                            <div className="flex gap-4">
                                <div className="flex items-center gap-2 text-[10px] text-gray-500">
                                    <div className="p-1 bg-white/5 rounded border border-white/10">↑↓</div>
                                    <span>Navigate</span>
                                </div>
                                <div className="flex items-center gap-2 text-[10px] text-gray-500">
                                    <div className="px-1.5 py-0.5 bg-white/5 rounded border border-white/10">Enter</div>
                                    <span>Execute</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-[9px] font-bold text-primary uppercase tracking-widest opacity-50">Terminal Excellence V3</span>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
});

CommandCenter.displayName = 'CommandCenter';
