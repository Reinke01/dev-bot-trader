
import { createContext, useContext, useState, type ReactNode, useCallback } from 'react';

export type WindowType = 'chart' | 'whale' | 'radar' | 'trades' | 'performance' | 'scanner' | 'ai' | 'signals' | 'config' | 'ticket';

export interface WindowState {
    id: string;
    type: WindowType;
    title: string;
    isOpen: boolean;
    zIndex: number;
    position: { x: number; y: number };
    size: { width: number; height: number };
    data?: any; // To pass specific data like 'symbol' to charts
}

interface WindowContextType {
    windows: WindowState[];
    openWindow: (type: WindowType, data?: any) => void;
    closeWindow: (id: string) => void;
    focusWindow: (id: string) => void;
    activeWindowId: string | null;
}

const WindowContext = createContext<WindowContextType | undefined>(undefined);

export const WindowProvider = ({ children }: { children: ReactNode }) => {
    const [windows, setWindows] = useState<WindowState[]>([
        // Initial Default Layout
        {
            id: 'chart-btc',
            type: 'chart',
            title: 'Chart - BTCUSDT',
            isOpen: true,
            zIndex: 10,
            position: { x: 50, y: 70 },
            size: { width: 800, height: 500 },
            data: { symbol: 'BTCUSDT' }
        },
        {
            id: 'whale-stream',
            type: 'whale',
            title: 'Whale Stream',
            isOpen: true,
            zIndex: 11,
            position: { x: 900, y: 70 },
            size: { width: 350, height: 400 },
            data: { symbol: 'BTCUSDT' }
        },
        {
            id: 'global-scanner',
            type: 'scanner',
            title: 'Market Scanner',
            isOpen: true,
            zIndex: 9,
            position: { x: 50, y: 600 },
            size: { width: 1200, height: 300 }
        }
    ]);

    const [maxZIndex, setMaxZIndex] = useState(20);
    const [activeWindowId, setActiveWindowId] = useState<string | null>('chart-btc');

    const focusWindow = useCallback((id: string) => {
        setWindows(prev => prev.map(w => {
            if (w.id === id) {
                const newZ = maxZIndex + 1;
                setMaxZIndex(newZ);
                return { ...w, zIndex: newZ };
            }
            return w;
        }));
        setActiveWindowId(id);
    }, [maxZIndex]);

    const openWindow = useCallback((type: WindowType, data?: any) => {
        // Prevent duplicate windows for single-instance tools
        const singleInstanceTypes = ['whale', 'radar', 'scanner', 'trades', 'performance', 'ai', 'signals', 'config'];
        if (singleInstanceTypes.includes(type)) {
            const existing = windows.find(w => w.type === type);
            if (existing) {
                focusWindow(existing.id);
                return;
            }
        }

        const id = `${type}-${Date.now()}`;
        const titleMap: Record<WindowType, string> = {
            chart: `Chart ${data?.symbol ? '- ' + data.symbol : ''}`,
            whale: 'Whale Stream',
            radar: 'Liquidation Radar',
            trades: 'Trade Manager',
            performance: 'Performance Stats',
            scanner: 'Market Scanner',
            ai: 'AI Pilot',
            signals: 'Signals',
            config: 'Global Config',
            ticket: 'Trade Ticket'
        };

        const newWindow: WindowState = {
            id,
            type,
            title: titleMap[type],
            isOpen: true,
            zIndex: maxZIndex + 1,
            position: { x: 100 + (windows.length * 30), y: 100 + (windows.length * 30) }, // Cascade
            size: { width: 600, height: 400 },
            data
        };

        setWindows(prev => [...prev, newWindow]);
        setMaxZIndex(prev => prev + 1);
        setActiveWindowId(id);
    }, [maxZIndex, windows.length]);

    const closeWindow = useCallback((id: string) => {
        setWindows(prev => prev.filter(w => w.id !== id));
        if (activeWindowId === id) setActiveWindowId(null);
    }, [activeWindowId]);

    return (
        <WindowContext.Provider value={{ windows, openWindow, closeWindow, focusWindow, activeWindowId }}>
            {children}
        </WindowContext.Provider>
    );
};

export const useWindowManager = () => {
    const context = useContext(WindowContext);
    if (!context) throw new Error("useWindowManager must be used within a WindowProvider");
    return context;
};
