
import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { WindowManagerProvider, useWindowManager } from './contexts/WindowManager';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';
import { useScanner, useWallet } from './hooks/useMarketData';
import { FloatingWindow } from './components/ui/FloatingWindow';
import { TradingChart } from './components/TradingChart';
import { WhaleStream } from './components/WhaleStream';
import { LiquidationRadar } from './components/LiquidationRadar';
import { HeatmapTable } from './components/HeatmapTable';
import { MonitoringPanel } from './components/MonitoringPanel';
import { TradeManagement } from './components/TradeManagement';
import { AIPilotSidebar } from './components/AIPilotSidebar';
import { TradeTicket } from './components/TradeTicket';
import { SignalsPanel } from './components/SignalsPanel';
import { ConfigModal } from './components/ConfigModal';
import { CommandCenter } from './components/CommandCenter';
import { LayoutGrid, Plus } from 'lucide-react';
import type { LogEntry, BotSummary, ScannerResult, GlobalConfig, PerformanceStats, TradeHistoryItem } from './types';

// Wrapper component to consume Contexts
const DesktopEnvironment = () => {
  const { windows, closeWindow, focusWindow, openWindow } = useWindowManager();
  const { t } = useLanguage();

  // App Global State (preserved from original App.tsx)
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [bots, setBots] = useState<BotSummary[]>([]);
  const [scannerData, setScannerData] = useState<ScannerResult[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState<'terminal' | 'bots' | 'performance'>('terminal');
  const [isConfiguring, setIsConfiguring] = useState(false);
  const [isCommandCenterOpen, setIsCommandCenterOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [scanLimit, setScanLimit] = useState(20);
  const [theme, setTheme] = useState<string>(() => localStorage.getItem('devbot_theme') || 'gold');
  const [isGlobalConfigOpen, setIsGlobalConfigOpen] = useState(false);
  const [globalConfig, setGlobalConfig] = useState<GlobalConfig>(() => {
    const saved = localStorage.getItem('terminal_config');
    try {
      return saved ? JSON.parse(saved) : { terminalMode: 'technical' };
    } catch {
      return { terminalMode: 'technical' };
    }
  });

  // Derived State (Mocked or Simplified for refactor speed)
  const [performanceStats, setPerformanceStats] = useState<PerformanceStats>({
    totalPnL: 0, winRate: 0, totalTrades: 0, profitFactor: 0
  });
  const [tradeHistory, setTradeHistory] = useState<TradeHistoryItem[]>([]);

  // TODO: Data Fetching logic (kept minimal for this step)
  // Re-implement or import the hooks/effects for data fetching here

  const renderWindowContent = (win: any) => {
    switch (win.type) {
      case 'chart':
        return <TradingChart symbol={win.data?.symbol || 'BTCUSDT'} />;
      case 'whale':
        return <WhaleStream symbol={win.data?.symbol || 'BTCUSDT'} />;
      case 'radar':
        return <LiquidationRadar />;
      case 'ticket':
        return (
          <TradeTicket
            symbol={win.data?.symbol || 'BTCUSDT'}
            currentPrice={win.data?.price || 100000} // Mock price for now
            onClose={() => closeWindow(win.id)}
          />
        );
      case 'scanner':
        return (
          <div className="p-2 h-full overflow-hidden">
            <HeatmapTable
              setSelectedSymbol={(sym) => openWindow('chart', { symbol: sym })}
              onOpenTicket={(sym, price) => openWindow('ticket', { symbol: sym, price })}
              scanLimit={scanLimit}
              terminalMode={globalConfig.terminalMode}
            />
          </div>
        );
      case 'trades':
        return (
          <TradeManagement
            bots={bots}
            history={tradeHistory}
            stats={performanceStats}
            stopBot={() => { }}
            terminalMode={globalConfig.terminalMode}
          />
        );
      default:
        return <div className="p-4 text-white/50">Component not implemented for {win.type}</div>;
    }
  };

  // Translate Window Titles
  const getTranslatedTitle = (win: any) => {
    if (win.type === 'whale') return t.dashboard.whaleStream;
    if (win.type === 'scanner') return t.dashboard.scanner;
    if (win.type === 'radar') return t.dashboard.liquidationRadar;
    if (win.type === 'ticket') return `Trade ${win.data?.symbol || ''}`;
    return win.TITLE_OVERRIDE || win.title;
  };

  // Data Hooks
  const { balance, equity } = useWallet();

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans overflow-hidden">
      <CommandCenter
        isOpen={isCommandCenterOpen}
        onClose={() => setIsCommandCenterOpen(false)}
        onExecute={() => { }}
        currentTheme={theme}
      />

      <Header
        search={search}
        setSearch={setSearch}
        isConnected={isConnected}
        isConfiguring={isConfiguring}
        setIsConfiguring={setIsConfiguring}
        scanLimit={scanLimit}
        updateLimit={setScanLimit}
        userName="DevTrader"
        theme={theme}
        setTheme={setTheme}
        openGlobalConfig={() => setIsGlobalConfigOpen(true)}
        terminalMode={globalConfig.terminalMode}
        onTerminalModeChange={(mode) => setGlobalConfig({ ...globalConfig, terminalMode: mode })}
        wallet={{ balance, equity }}
      />

      <ConfigModal
        isOpen={isGlobalConfigOpen}
        onClose={() => setIsGlobalConfigOpen(false)}
        onConfigChange={setGlobalConfig}
      />

      {/* Dock / Taskbar */}
      <div className="h-10 bg-[#0a0a0a] border-b border-white/5 flex items-center px-4 gap-2">
        <button onClick={() => openWindow('chart', { symbol: 'BTCUSDT' })} className="flex items-center gap-1 px-3 py-1 bg-white/5 hover:bg-white/10 rounded text-xs transition-colors">
          <Plus className="w-3 h-3" /> {t.dashboard.newChart}
        </button>
        <button onClick={() => openWindow('whale')} className="flex items-center gap-1 px-3 py-1 bg-white/5 hover:bg-white/10 rounded text-xs transition-colors">
          {t.dashboard.whaleStream}
        </button>
        <button onClick={() => openWindow('scanner')} className="flex items-center gap-1 px-3 py-1 bg-white/5 hover:bg-white/10 rounded text-xs transition-colors">
          {t.dashboard.scanner}
        </button>
      </div>

      {/* Desktop Area */}
      <div className="flex-1 relative bg-[url('/grid-pattern.png')] bg-repeat opacity-100"
        style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.05) 1px, transparent 0)', backgroundSize: '24px 24px' }}>

        {windows.map(win => (
          <FloatingWindow
            key={win.id}
            id={win.id}
            title={getTranslatedTitle(win)}
            isOpen={win.isOpen}
            onClose={() => closeWindow(win.id)}
            onFocus={() => focusWindow(win.id)}
            zIndex={win.zIndex}
            initialPosition={win.position}
            initialSize={win.size}
          >
            {renderWindowContent(win)}
          </FloatingWindow>
        ))}
      </div>
    </div>
  );
};

function App() {
  return (
    <LanguageProvider>
      <WindowManagerProvider>
        <DesktopEnvironment />
      </WindowManagerProvider>
    </LanguageProvider>
  );
}

export default App;
