import { memo, useEffect, useRef } from 'react';

interface TradingChartProps {
    symbol: string;
}

export const TradingChart = memo(({ symbol }: TradingChartProps) => {
    const container = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!container.current) return;

        // Clear previous chart
        container.current.innerHTML = '';

        const script = document.createElement("script");
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
        script.type = "text/javascript";
        script.async = true;
        script.innerHTML = JSON.stringify({
            "autosize": true,
            "symbol": `BINANCE:${symbol}`,
            "interval": "15",
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "enable_publishing": false,
            "hide_top_toolbar": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "save_image": true,
            "details": true,
            "hotlist": true,
            "calendar": false,
            "show_popup_button": true,
            "popup_width": "1000",
            "popup_height": "650",
            "support_host": "https://www.tradingview.com"
        });

        container.current.appendChild(script);
    }, [symbol]);

    return (
        <div className="w-full h-full bg-black/40">
            <div className="tradingview-widget-container h-full w-full" ref={container}>
                <div className="tradingview-widget-container__widget h-full w-full"></div>
            </div>
        </div>
    );
});

TradingChart.displayName = 'TradingChart';
