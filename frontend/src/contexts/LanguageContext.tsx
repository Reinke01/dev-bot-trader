
import { createContext, useContext, useState, type ReactNode } from 'react';

type Language = 'pt' | 'en' | 'es';

type Translations = {
    [key in Language]: {
        dashboard: {
            newChart: string;
            whaleStream: string;
            scanner: string;
            liquidationRadar: string;
            pnlHistory: string;
            activeTrades: string;
            fearGreed: string;
        };
        fearGreed: {
            extremeFear: string;
            fear: string;
            neutral: string;
            greed: string;
            extremeGreed: string;
        };
        common: {
            loading: string;
            error: string;
            buy: string;
            sell: string;
        };
        ticket: {
            price: string;
            amount: string;
            buyLong: string;
            sellShort: string;
            leverage: string;
            cost: string;
            value: string;
            actionBuy: string;
            actionSell: string;
            typeLimit: string;
            typeMarket: string;
        };
        table: {
            asset: string;
            score: string;
            rsi: string;
            factors: string;
            price: string;
            action: string;
        };
        header: {
            balance: string;
            equity: string;
            filter: string;
            essential: string;
            technical: string;
            apiLive: string;
            offline: string;
            configTitle: string;
            configDesc: string;
            symbols: string;
            globalSettings: string;
        };
    }
};

const translations: Translations = {
    pt: {
        dashboard: {
            newChart: 'Novo Gráfico',
            whaleStream: 'Fluxo de Baleias',
            scanner: 'Scanner de Mercado',
            liquidationRadar: 'Radar de Liquidação',
            pnlHistory: 'Histórico de Lucro',
            activeTrades: 'Trades Ativos',
            fearGreed: 'Termômetro do Mercado'
        },
        fearGreed: {
            extremeFear: 'Medo Extremo',
            fear: 'Medo',
            neutral: 'Neutro',
            greed: 'Ganância',
            extremeGreed: 'Ganância Extrema'
        },
        common: {
            loading: 'Carregando...',
            error: 'Erro',
            buy: 'Compra',
            sell: 'Venda'
        },
        ticket: {
            price: 'Preço',
            amount: 'Quant.',
            buyLong: 'Compra / Long',
            sellShort: 'Venda / Short',
            leverage: 'Alavancagem',
            cost: 'Custo',
            value: 'Valor',
            actionBuy: 'Comprar',
            actionSell: 'Vender',
            typeLimit: 'Limite',
            typeMarket: 'Mercado'
        },
        table: {
            asset: 'Ativo',
            score: 'Score IA',
            rsi: 'RSI',
            factors: 'Fatores',
            price: 'Preço',
            action: 'Ação'
        },
        header: {
            balance: 'Saldo',
            equity: 'Patrimônio',
            filter: 'Filtrar símbolos...',
            essential: 'Essencial',
            technical: 'Técnico',
            apiLive: 'API Online',
            offline: 'Offline',
            configTitle: 'Capacidade do Scanner',
            configDesc: 'Monitorar moedas em tempo real (Max 160). Reduzir economiza recursos.',
            symbols: 'Símbolos',
            globalSettings: 'Configuração Global API'
        }
    },
    en: {
        dashboard: {
            newChart: 'New Chart',
            whaleStream: 'Whale Stream',
            scanner: 'Market Scanner',
            liquidationRadar: 'Liquidation Radar',
            pnlHistory: 'PnL History',
            activeTrades: 'Active Trades',
            fearGreed: 'Market Thermometer'
        },
        fearGreed: {
            extremeFear: 'Extreme Fear',
            fear: 'Fear',
            neutral: 'Neutral',
            greed: 'Greed',
            extremeGreed: 'Extreme Greed'
        },
        common: {
            loading: 'Loading...',
            error: 'Error',
            buy: 'Buy',
            sell: 'Sell'
        },
        ticket: {
            price: 'Price',
            amount: 'Amount',
            buyLong: 'Buy / Long',
            sellShort: 'Sell / Short',
            leverage: 'Leverage',
            cost: 'Cost',
            value: 'Value',
            actionBuy: 'Buy',
            actionSell: 'Sell',
            typeLimit: 'Limit',
            typeMarket: 'Market'
        },
        table: {
            asset: 'Asset',
            score: 'AI Score',
            rsi: 'RSI',
            factors: 'Factors',
            price: 'Price',
            action: 'Action'
        },
        header: {
            balance: 'Balance',
            equity: 'Equity',
            filter: 'Filter symbols...',
            essential: 'Essential',
            technical: 'Technical',
            apiLive: 'API Live',
            offline: 'Offline',
            configTitle: 'Scanner Capacity',
            configDesc: 'Monitor real-time coins (Max 160). Reducing saves resources.',
            symbols: 'Symbols',
            globalSettings: 'Global API Settings'
        }
    },
    es: {
        dashboard: {
            newChart: 'Nuevo Gráfico',
            whaleStream: 'Flujo de Ballenas',
            scanner: 'Escáner de Mercado',
            liquidationRadar: 'Radar de Liquidación',
            pnlHistory: 'Historial PnL',
            activeTrades: 'Operaciones Activas',
            fearGreed: 'Termómetro del Mercado'
        },
        fearGreed: {
            extremeFear: 'Miedo Extremo',
            fear: 'Miedo',
            neutral: 'Neutral',
            greed: 'Avaricia',
            extremeGreed: 'Avaricia Extrema'
        },
        common: {
            loading: 'Cargando...',
            error: 'Error',
            buy: 'Compra',
            sell: 'Venta'
        },
        ticket: {
            price: 'Precio',
            amount: 'Cant.',
            buyLong: 'Compra / Long',
            sellShort: 'Venta / Corto',
            leverage: 'Apalancamiento',
            cost: 'Costo',
            value: 'Valor',
            actionBuy: 'Comprar',
            actionSell: 'Vender',
            typeLimit: 'Límite',
            typeMarket: 'Mercado'
        },
        table: {
            asset: 'Activo',
            score: 'Puntaje IA',
            rsi: 'RSI',
            factors: 'Factores',
            price: 'Precio',
            action: 'Acción'
        },
        header: {
            balance: 'Saldo',
            equity: 'Patrimonio',
            filter: 'Filtrar símbolos...',
            essential: 'Esencial',
            technical: 'Técnico',
            apiLive: 'API Conectada',
            offline: 'Desconectado',
            configTitle: 'Capacidad del Escáner',
            configDesc: 'Monitorear monedas en tiempo real (Max 160). Reducir ahorra recursos.',
            symbols: 'Símbolos',
            globalSettings: 'Configuración Global API'
        }
    }
};

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: Translations['pt'];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
    const [language, setLanguage] = useState<Language>('pt');

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t: translations[language] }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) throw new Error('useLanguage must be used within a LanguageProvider');
    return context;
};
