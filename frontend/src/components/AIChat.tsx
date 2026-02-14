import { useState, useRef, useEffect, memo } from 'react';
import { MessageSquare, X, Send, Sparkles, TrendingUp, Settings, BrainCircuit, Cpu, Globe, Key, ShieldCheck, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { ScannerResult } from '../types';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface AIConfig {
    provider: 'groq' | 'gemini' | 'openai' | 'local' | 'deepseek' | 'ollama';
    apiKey: string;
    model: string;
}

interface AIChatProps {
    scannerData: ScannerResult[];
}

export const AIChat = memo(({ scannerData }: AIChatProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [config, setConfig] = useState<AIConfig>(() => {
        const saved = localStorage.getItem('antigravity_ai_config');
        return saved ? JSON.parse(saved) : {
            provider: 'local',
            apiKey: '',
            model: 'llama-3-quant'
        };
    });

    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: "Olá! Sou o Reinke AI. Estou monitorando o mercado agora. No painel 'AI Opportunities' ao lado, você verá as melhores entradas. Clique em 'Aprovar' para iniciar o bot imediatamente!",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        localStorage.setItem('antigravity_ai_config', JSON.stringify(config));
    }, [config]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            role: 'user',
            content: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        // Actual AI API Logic
        try {
            let response = "";
            const upperInput = input.toUpperCase();

            if (config.provider === 'local') {
                const mentionedAsset = scannerData.find(s => upperInput.includes(s.symbol));

                if (upperInput.includes("DAY TRADE") || upperInput.includes("CURTO PRAZO")) {
                    const top = [...scannerData].sort((a, b) => b.score - a.score)[0];
                    response = top
                        ? `[DAY TRADE] ⚡ Foco no momentum imediato: ${top.symbol} está com Score ${top.score}/5 e RSI ${top.rsi}. Ideal para scalping ou trades rápidos de 15m a 1h.`
                        : "Buscando alvos de Day Trade...";
                } else if (upperInput.includes("SWING TRADE") || upperInput.includes("LONGO PRAZO")) {
                    const stable = [...scannerData].filter(s => s.score >= 3).sort((a, b) => a.rsi - b.rsi)[0];
                    response = stable
                        ? `[SWING TRADE] 📈 Foco em tendência e reversão: ${stable.symbol} (Score ${stable.score}, RSI ${stable.rsi}) mostra estrutura sólida para trades de 4h a 1D.`
                        : "Buscando alvos de Swing Trade...";
                } else if (upperInput.includes("MELHORES") || upperInput.includes("OPORTUNIDADE") || upperInput.includes("RECOMENDAR")) {
                    const best = [...scannerData]
                        .sort((a, b) => b.score - a.score)
                        .slice(0, 3);

                    if (best.length > 0) {
                        response = `[QUANT ANALYST] 🎯 TOP PICKS DETECTADOS:\n` +
                            best.map(s => `• ${s.symbol}: Score ${s.score}/5. Já disponível para aprovação no painel lateral!`).join('\n') +
                            ` \n\nEstratégia recomendada: Clique em 'Aprovar' no painel de Oportunidades para o bot assumir a execução.`;
                    } else {
                        response = "O scanner ainda está carregando dados. Aguarde um momento para uma análise precisa.";
                    }
                } else if (mentionedAsset) {
                    const momentum = mentionedAsset.score >= 4 ? "Forte" : "Moderado";
                    response = `[LOCAL ANALYST] Par ${mentionedAsset.symbol}: Score ${mentionedAsset.score}/5, RSI ${mentionedAsset.rsi}. Momentum ${momentum}. Probabilidade Técnica: ${(mentionedAsset.score * 12 + 40).toFixed(1)}%.`;
                } else {
                    response = "Estou em modo Local. Tente 'Melhores Oportunidades', 'Day Trade' ou 'Swing Trade'.";
                }
            } else {
                const context = `
                    DADOS ATUAIS DO MERCADO (RANKING):
                    ${[...scannerData].sort((a, b) => b.score - a.score).slice(0, 10).map(s => `${s.symbol}: Score ${s.score}/5, RSI ${s.rsi}`).join('\n')}
                `;

                const prompt = `Você é um analista quantitativo de crypto profissional (ESTILO TRADER ESPORTIVO/QUANT). 
                DADOS DO SCANNER: ${context}. 
                OBJETIVO:
                - Se o usuário pedir 'Day Trade', foque em ativos com Score alto (4+) e RSI extremo (acima de 70 para venda, abaixo de 30 para compra) para movimentos rápidos de poucos minutos/horas.
                - Se pedir 'Swing Trade', foque em ativos com Score estável (3+) e RSI em zona neutra (40-60) indicando início de tendência para dias.
                - Se pedir 'Recomendar' ou 'Oportunidade', dê os 3 nomes mais quentes do scanner agora e explique o porquê técnico (Score de tendência + RSI de momento).
                USUÁRIO: ${input}. 
                Responda de forma curta, impactante e técnica em Português.`;

                if (config.provider === 'groq') {
                    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${config.apiKey}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            model: "llama3-8b-8192",
                            messages: [{ role: "user", content: prompt }]
                        })
                    });
                    const data = await res.json();
                    response = data.choices[0].message.content;
                } else if (config.provider === 'gemini') {
                    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${config.apiKey}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            contents: [{ parts: [{ text: prompt }] }]
                        })
                    });
                    const data = await res.json();
                    response = data.candidates[0].content.parts[0].text;
                } else if (config.provider === 'openai') {
                    const res = await fetch('https://api.openai.com/v1/chat/completions', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${config.apiKey}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            model: "gpt-4o",
                            messages: [{ role: "user", content: prompt }]
                        })
                    });
                    const data = await res.json();
                    response = data.choices[0].message.content;
                } else if (config.provider === 'deepseek') {
                    const res = await fetch('https://api.deepseek.com/chat/completions', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${config.apiKey}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            model: "deepseek-chat",
                            messages: [{ role: "user", content: prompt }]
                        })
                    });
                    const data = await res.json();
                    response = data.choices[0].message.content;
                } else if (config.provider === 'ollama') {
                    const res = await fetch('http://localhost:11434/api/chat', {
                        method: 'POST',
                        body: JSON.stringify({
                            model: "llama3",
                            messages: [{ role: "user", content: prompt }],
                            stream: false
                        })
                    });
                    const data = await res.json();
                    response = data.message.content;
                }
            }

            const botMsg: Message = {
                role: 'assistant',
                content: response,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Erro ao conectar com a API. Verifique sua chave e conexão.",
                timestamp: new Date()
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-[200]">
            <AnimatePresence>
                {isOpen ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="w-[450px] h-[650px] glass border border-primary/20 rounded-2xl flex flex-col shadow-2xl overflow-hidden bg-[#0a0a0c]/95 backdrop-blur-2xl"
                    >
                        {/* Header */}
                        <div className="p-5 border-b border-white/5 bg-gradient-to-r from-primary/10 to-transparent flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="p-2.5 bg-primary rounded-xl shadow-[0_0_20px_rgba(255,215,0,0.3)] border border-white/10">
                                    <BrainCircuit className="w-5 h-5 text-background" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-sm text-primary uppercase tracking-[0.2em] leading-none mb-1">Dev Bot AI</h3>
                                    <div className="flex items-center gap-2">
                                        <span className="flex h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                                        <span className="text-[9px] text-gray-500 font-mono uppercase tracking-widest">
                                            {config.provider === 'local' ? 'Local Intelligence' : `${config.provider} Active`}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={() => setShowSettings(!showSettings)}
                                    className={cn(
                                        "p-2 rounded-lg transition-all",
                                        showSettings ? "bg-primary text-background" : "hover:bg-white/5 text-gray-500"
                                    )}
                                >
                                    <Settings className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="p-2 hover:bg-danger/20 rounded-lg text-gray-500 hover:text-danger transition-all"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                        </div>

                        {/* Content Area */}
                        <div className="flex-1 overflow-hidden relative flex flex-col">
                            {/* Settings Overlay */}
                            <AnimatePresence>
                                {showSettings && (
                                    <motion.div
                                        initial={{ x: '100%' }}
                                        animate={{ x: 0 }}
                                        exit={{ x: '100%' }}
                                        className="absolute inset-0 z-50 bg-[#0a0a0c] p-6 space-y-6"
                                    >
                                        <div className="flex items-center justify-between mb-4">
                                            <h4 className="text-xs font-bold text-primary uppercase tracking-widest flex items-center gap-2">
                                                <Cpu className="w-4 h-4" /> AI Configuration
                                            </h4>
                                            <button onClick={() => setShowSettings(false)} className="text-gray-500 hover:text-white">
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>

                                        <div className="space-y-4">
                                            <div>
                                                <label className="text-[10px] text-gray-500 uppercase block mb-1.5">Provider</label>
                                                <div className="grid grid-cols-3 gap-2">
                                                    {(['local', 'gemini', 'groq', 'deepseek', 'ollama', 'openai'] as const).map(p => (
                                                        <button
                                                            key={p}
                                                            onClick={() => setConfig({ ...config, provider: p })}
                                                            className={cn(
                                                                "px-2 py-2 rounded-lg text-[10px] font-bold uppercase transition-all border break-all",
                                                                config.provider === p
                                                                    ? "bg-primary/20 border-primary text-primary"
                                                                    : "bg-white/5 border-white/5 text-gray-500 hover:bg-white/10"
                                                            )}
                                                        >
                                                            {p}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>

                                            {config.provider !== 'local' && (
                                                <div className="space-y-3 pt-2">
                                                    <div>
                                                        <label className="text-[10px] text-gray-500 uppercase block mb-1.5 flex items-center gap-2">
                                                            <Key className="w-3 h-3" /> API Key
                                                        </label>
                                                        <input
                                                            type="password"
                                                            value={config.apiKey}
                                                            onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                                                            placeholder={`Paste your ${config.provider} key...`}
                                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs outline-none focus:border-primary/50"
                                                        />
                                                    </div>
                                                    <div className="p-3 rounded-lg bg-success/5 border border-success/20">
                                                        <p className="text-[10px] text-success italic flex items-center gap-2">
                                                            <ShieldCheck className="w-3 h-3" /> Keys are stored locally in your browser.
                                                        </p>
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        <button
                                            onClick={() => setShowSettings(false)}
                                            className="w-full py-3 bg-primary text-background font-bold text-[10px] uppercase tracking-widest rounded-xl hover:scale-[1.02] transition-transform mt-auto"
                                        >
                                            Save Parameters
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Chat Messages */}
                            <div
                                ref={scrollRef}
                                className="flex-1 overflow-auto p-5 space-y-5 custom-scrollbar"
                            >
                                {config.provider === 'local' && (
                                    <div className="mx-5 mb-4 p-4 rounded-xl bg-primary/10 border border-primary/20 animate-pulse">
                                        <p className="text-[10px] text-primary font-bold uppercase mb-2">🚀 Upgrade Disponível</p>
                                        <p className="text-[11px] text-gray-300 leading-relaxed mb-3">
                                            Conecte uma API Key (Groq/Gemini) para liberar análises profundas de Day Trade e Swing Trade com IA Master.
                                        </p>
                                        <button
                                            onClick={() => setShowSettings(true)}
                                            className="px-4 py-2 bg-primary text-background rounded-lg text-[10px] font-black uppercase tracking-tighter"
                                        >
                                            Configurar API Agora
                                        </button>
                                    </div>
                                )}
                                {messages.map((msg, i) => (
                                    <div
                                        key={i}
                                        className={cn(
                                            "flex flex-col max-w-[88%] animate-in fade-in slide-in-from-bottom-2 duration-300",
                                            msg.role === 'user' ? "ml-auto items-end" : "items-start"
                                        )}
                                    >
                                        <div className={cn(
                                            "p-4 rounded-2xl text-[12px] leading-relaxed shadow-xl",
                                            msg.role === 'user'
                                                ? "bg-primary text-background font-medium rounded-tr-none"
                                                : "bg-white/[0.03] border border-white/5 text-gray-200 rounded-tl-none backdrop-blur-md"
                                        )}>
                                            {msg.content}
                                        </div>
                                        <span className="text-[9px] text-gray-600 mt-1.5 font-mono uppercase tracking-tighter">
                                            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                ))}
                                {isTyping && (
                                    <div className="flex items-center gap-3 py-2">
                                        <div className="flex gap-1">
                                            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></span>
                                        </div>
                                        <span className="text-[10px] text-primary/70 uppercase font-bold tracking-[0.2em] italic">Quant Engine Active...</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Input Area */}
                        <div className="p-5 bg-black/60 border-t border-white/5 backdrop-blur-md">
                            <div className="relative group">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Perguntar sobre momentum ou backtest..."
                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-xs outline-none focus:border-primary/50 focus:bg-white/[0.08] transition-all pr-14 placeholder:text-gray-600"
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={!input.trim()}
                                    className="absolute right-2.5 top-2.5 p-2 bg-primary text-background rounded-lg hover:scale-105 active:scale-95 disabled:opacity-30 disabled:hover:scale-100 transition-all shadow-lg shadow-primary/30"
                                >
                                    <Send className="w-4.5 h-4.5" />
                                </button>
                            </div>
                            <div className="flex gap-2 mt-4 overflow-x-auto pb-1 no-scrollbar">
                                <button
                                    onClick={() => setInput("Melhores Oportunidades Agora")}
                                    className="whitespace-nowrap bg-success/10 hover:bg-success/20 text-success text-[9px] font-bold uppercase px-3 py-1.5 rounded-lg border border-success/20 transition-all flex items-center gap-2"
                                >
                                    <Sparkles className="w-3.5 h-3.5" /> Oportunidades 🎯
                                </button>
                                <button
                                    onClick={() => setInput("Análise de Day Trade")}
                                    className="whitespace-nowrap bg-danger/10 hover:bg-danger/20 text-danger text-[9px] font-bold uppercase px-3 py-1.5 rounded-lg border border-danger/20 transition-all flex items-center gap-2"
                                >
                                    <Zap className="w-3.5 h-3.5" /> Day Trade
                                </button>
                                <button
                                    onClick={() => setInput("Análise de Swing Trade")}
                                    className="whitespace-nowrap bg-secondary/10 hover:bg-secondary/20 text-secondary text-[9px] font-bold uppercase px-3 py-1.5 rounded-lg border border-secondary/20 transition-all flex items-center gap-2"
                                >
                                    <TrendingUp className="w-3.5 h-3.5" /> Swing Trade
                                </button>
                                <button
                                    onClick={() => setInput("Simular Backtest de 3 dias")}
                                    className="whitespace-nowrap bg-white/5 hover:bg-white/10 text-gray-400 text-[9px] font-bold uppercase px-3 py-1.5 rounded-lg border border-white/10 transition-all flex items-center gap-2"
                                >
                                    <Globe className="w-3.5 h-3.5" /> Global Hist.
                                </button>
                            </div>
                        </div>
                    </motion.div>
                ) : (
                    <motion.button
                        initial={{ scale: 0, rotate: -45 }}
                        animate={{ scale: 1, rotate: 0 }}
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => setIsOpen(true)}
                        className="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-background shadow-[0_0_40px_rgba(255,215,0,0.4)] relative group border-4 border-[#0a0a0c]"
                    >
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-success rounded-full border-4 border-[#0a0a0c] shadow-lg animate-pulse" />
                        <MessageSquare className="w-7 h-7 group-hover:hidden" />
                        <BrainCircuit className="w-7 h-7 hidden group-hover:block animate-in zoom-in-50 duration-300" />
                    </motion.button>
                )}
            </AnimatePresence>
        </div>
    );
});

AIChat.displayName = 'AIChat';
