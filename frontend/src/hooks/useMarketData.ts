
import { useState, useEffect } from 'react';

// Mocked for now, but ready to be replaced with real API calls using fetch/axios
const API_BASE = 'http://localhost:8000/api/v1';

export interface ScannerData {
    symbol: string;
    price: number;
    change24h: number;
    volume24h: number;
    score: number; // AI Score (0-100)
    signal: 'buy' | 'sell' | 'neutral';
    rsi: number;
    factors: { [key: string]: boolean };
}

export const useScanner = () => {
    const [data, setData] = useState<ScannerData[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchScanner = async () => {
        try {
            // TODO: Replace with real fetch
            // const res = await fetch(`${API_BASE}/scanner`);
            // const json = await res.json();

            // Temporary Mock to simulate "Professional" AI Score
            const mockData: ScannerData[] = Array.from({ length: 20 }).map((_, i) => ({
                symbol: ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'LTC', 'BCH', 'ATOM', 'XLM', 'NEAR', 'QNT', 'AAVE', 'ALGO', 'FIL'][i] + 'USDT',
                price: Math.random() * 1000 + 10,
                change24h: (Math.random() * 10) - 5,
                volume24h: Math.floor(Math.random() * 10000000),
                score: Math.floor(Math.random() * 40) + 60, // High score for top opportunities
                signal: (Math.random() > 0.6 ? 'buy' : Math.random() > 0.8 ? 'sell' : 'neutral') as 'buy' | 'sell' | 'neutral',
                rsi: Math.floor(Math.random() * 100),
                factors: { 'Trend': true, 'Vol': Math.random() > 0.5, 'Mom': true }
            })).sort((a, b) => b.score - a.score);

            setData(mockData);
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch scanner:", error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchScanner();
        const interval = setInterval(fetchScanner, 5000); // Live update
        return () => clearInterval(interval);
    }, []);

    return { data, loading };
};

export const useWallet = () => {
    const [balance, setBalance] = useState(0);
    const [equity, setEquity] = useState(0);

    // Simulate fetching wallet data
    useEffect(() => {
        setBalance(10543.20);
        setEquity(10890.50); // Little profit
    }, []);

    return { balance, equity };
};
