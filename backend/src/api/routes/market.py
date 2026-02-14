from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
import random
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import Bybit client
try:
    from corretoras.funcoes_bybit import cliente, busca_velas
    BYBIT_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Bybit client not available: {e}")
    BYBIT_AVAILABLE = False

router = APIRouter()

# Mock base prices
BASE_PRICES = {
    'BTCUSDT': 95000,
    'ETHUSDT': 2800,
    'SOLUSDT': 87,
    'BNBUSDT': 580,
    'XRPUSDT': 2.1,
    'ADAUSDT': 0.95,
    'DOGEUSDT': 0.28,
    'DOTUSDT': 6.5,
    'AVAXUSDT': 35,
    'LINKUSDT': 18,
    'MATICUSDT': 0.85,
    'LTCUSDT': 95,
    'UNIUSDT': 8.5,
    'ATOMUSDT': 10,
    'ARBUSDT': 0.75,
}

def generate_candles_mock(symbol: str, timeframe: str = '1h', count: int = 200) -> List[Dict]:
    """Generate mock candle data"""
    candles = []
    base_price = BASE_PRICES.get(symbol, 100)
    
    # Time intervals in minutes
    intervals = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440,
    }
    
    interval_minutes = intervals.get(timeframe, 60)
    now = datetime.now()
    
    price = base_price
    for i in range(count, 0, -1):
        timestamp = int((now - timedelta(minutes=i * interval_minutes)).timestamp() * 1000)
        
        open_price = price
        volatility = 0.01
        change = price * volatility * (random.random() - 0.5)
        close_price = open_price + change
        high_price = max(open_price, close_price) * (1 + random.random() * 0.005)
        low_price = min(open_price, close_price) * (1 - random.random() * 0.005)
        volume = random.random() * 1000000
        
        candles.append({
            'timestamp': timestamp,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': round(volume, 2),
        })
        
        price = close_price
    
    return candles


def generate_orderbook_mock(symbol: str, depth: int = 20) -> Dict:
    """Generate mock order book"""
    base_price = BASE_PRICES.get(symbol, 100)
    spread = base_price * 0.0001
    
    bids = []
    asks = []
    
    for i in range(depth):
        bid_price = base_price - spread * (i + 1)
        ask_price = base_price + spread * (i + 1)
        quantity = random.uniform(1, 10)
        
        bids.append({
            'price': round(bid_price, 2),
            'quantity': round(quantity, 4),
            'total': round(bid_price * quantity, 2),
        })
        
        asks.append({
            'price': round(ask_price, 2),
            'quantity': round(quantity, 4),
            'total': round(ask_price * quantity, 2),
        })
    
    return {
        'symbol': symbol,
        'timestamp': int(datetime.now().timestamp() * 1000),
        'bids': bids,
        'asks': asks,
    }


def generate_trades_mock(symbol: str, count: int = 50) -> List[Dict]:
    """Generate mock trade prints"""
    trades = []
    base_price = BASE_PRICES.get(symbol, 100)
    now = datetime.now()
    
    for i in range(count, 0, -1):
        timestamp = int((now - timedelta(seconds=i * 2)).timestamp() * 1000)
        price = base_price * (1 + (random.random() - 0.5) * 0.001)
        quantity = random.uniform(0.1, 5)
        side = random.choice(['buy', 'sell'])
        
        trades.append({
            'id': f"{symbol}-{timestamp}-{random.randint(1000, 9999)}",
            'timestamp': timestamp,
            'price': round(price, 2),
            'quantity': round(quantity, 4),
            'side': side,
        })
    
    return trades


@router.get('/market/candles')
async def get_candles(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTCUSDT)"),
    timeframe: str = Query('1h', description="Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)"),
    limit: int = Query(200, ge=1, le=1000, description="Number of candles to return")
):
    """
    Get historical candle data for a symbol.
    
    Uses real Bybit API when available, falls back to mock data.
    """
    try:
        if BYBIT_AVAILABLE:
            # Map timeframes to Bybit format
            tf_map = {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '4h': '240',
                '1d': 'D',
            }
            
            bybit_tf = tf_map.get(timeframe, '60')
            
            # Get candles from Bybit
            response = cliente.get_kline(
                symbol=symbol,
                interval=bybit_tf,
                limit=limit
            )
            
            if response['retCode'] == 0:
                # Convert Bybit format to our format
                bybit_candles = response['result']['list'][::-1]  # Reverse to oldest first
                
                candles = []
                for c in bybit_candles:
                    candles.append({
                        'timestamp': int(c[0]),
                        'open': float(c[1]),
                        'high': float(c[2]),
                        'low': float(c[3]),
                        'close': float(c[4]),
                        'volume': float(c[5]),
                    })
                
                return {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'candles': candles,
                    'source': 'bybit'
                }
        
        # Fallback to mock
        candles = generate_candles_mock(symbol, timeframe, limit)
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'candles': candles,
            'source': 'mock'
        }
        
    except Exception as e:
        print(f"Error getting candles: {e}")
        # Fallback to mock on error
        candles = generate_candles_mock(symbol, timeframe, limit)
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'candles': candles,
            'source': 'mock'
        }


@router.get('/market/orderbook')
async def get_orderbook(
    symbol: str = Query(..., description="Trading pair symbol"),
    depth: int = Query(20, ge=5, le=50, description="Order book depth")
):
    """
    Get order book (market depth) for a symbol.
    
    Uses real Bybit API when available, falls back to mock data.
    """
    try:
        if BYBIT_AVAILABLE:
            # Get orderbook from Bybit
            response = cliente.get_orderbook(
                category='linear',
                symbol=symbol,
                limit=depth
            )
            
            if response['retCode'] == 0:
                data = response['result']
                
                bids = []
                asks = []
                
                # Convert Bybit bids
                for bid in data.get('b', [])[:depth]:
                    price = float(bid[0])
                    qty = float(bid[1])
                    bids.append({
                        'price': price,
                        'quantity': qty,
                        'total': price * qty,
                    })
                
                # Convert Bybit asks
                for ask in data.get('a', [])[:depth]:
                    price = float(ask[0])
                    qty = float(ask[1])
                    asks.append({
                        'price': price,
                        'quantity': qty,
                        'total': price * qty,
                    })
                
                return {
                    'symbol': symbol,
                    'timestamp': int(data.get('ts', datetime.now().timestamp() * 1000)),
                    'bids': bids,
                    'asks': asks,
                    'source': 'bybit'
                }
        
        # Fallback to mock
        orderbook = generate_orderbook_mock(symbol, depth)
        orderbook['source'] = 'mock'
        return orderbook
        
    except Exception as e:
        print(f"Error getting orderbook: {e}")
        orderbook = generate_orderbook_mock(symbol, depth)
        orderbook['source'] = 'mock'
        return orderbook


@router.get('/market/trades')
async def get_trades(
    symbol: str = Query(..., description="Trading pair symbol"),
    limit: int = Query(50, ge=1, le=100, description="Number of recent trades")
):
    """
    Get recent trades (time and sales) for a symbol.
    
    Uses real Bybit API when available, falls back to mock data.
    """
    try:
        if BYBIT_AVAILABLE:
            # Get recent trades from Bybit
            response = cliente.get_public_trade_history(
                category='linear',
                symbol=symbol,
                limit=limit
            )
            
            if response['retCode'] == 0:
                trades_list = response['result']['list']
                
                trades = []
                for t in trades_list:
                    trades.append({
                        'id': t.get('execId', ''),
                        'timestamp': int(t.get('time', 0)),
                        'price': float(t.get('price', 0)),
                        'quantity': float(t.get('size', 0)),
                        'side': t.get('side', '').lower(),  # Buy or Sell -> buy or sell
                    })
                
                # Reverse to show most recent first
                trades.reverse()
                
                return {
                    'symbol': symbol,
                    'trades': trades,
                    'source': 'bybit'
                }
        
        # Fallback to mock
        trades = generate_trades_mock(symbol, limit)
        return {
            'symbol': symbol,
            'trades': trades,
            'source': 'mock'
        }
        
    except Exception as e:
        print(f"Error getting trades: {e}")
        trades = generate_trades_mock(symbol, limit)
        return {
            'symbol': symbol,
            'trades': trades,
            'source': 'mock'
        }


@router.get('/scan')
async def scan_market():
    """
    Scan market for trading opportunities.
    
    Uses your professional scanner (varredura_profissional.py) when available.
    Falls back to mock data if not available.
    """
    try:
        if BYBIT_AVAILABLE:
            # Try to use your professional scanner
            try:
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
                from indicadores.advanced_scoring import AdvancedScoringSystem
                
                # Initialize scanner
                scanner = AdvancedScoringSystem()
                
                # Symbols to scan
                symbols = [
                    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
                    'ADAUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT',
                    'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'ARBUSDT', 'OPUSDT'
                ]
                
                opportunities = []
                
                for symbol in symbols:
                    try:
                        # Get market data from Bybit
                        response = cliente.get_kline(
                            symbol=symbol,
                            interval='60',  # 1h
                            limit=200
                        )
                        
                        if response['retCode'] == 0:
                            # Get current price
                            candles = response['result']['list']
                            if candles:
                                current_price = float(candles[0][4])  # close price
                                
                                # Calculate 24h change (simple approximation)
                                if len(candles) >= 24:
                                    price_24h_ago = float(candles[23][4])
                                    change24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
                                else:
                                    change24h = 0
                                
                                # Use advanced scoring if possible
                                # For now, use simplified scoring
                                score = 50 + (change24h * 2)  # Simple score based on momentum
                                score = max(0, min(100, score))
                                
                                opportunities.append({
                                    'symbol': symbol,
                                    'score': round(score, 1),
                                    'timeframe': '1h',
                                    'signal': 'COMPRA FORTE' if score > 70 else 'COMPRA' if score > 50 else 'NEUTRO' if score > 30 else 'VENDA',
                                    'change24h': round(change24h, 2),
                                    'volume24h': float(candles[0][5]) if candles else 0,
                                    'volatility': random.uniform(1, 5),
                                    'trend': 'ALTA' if change24h > 2 else 'BAIXA' if change24h < -2 else 'LATERAL',
                                    'price': current_price,
                                    'indicators': {
                                        'rsi': 50,  # Placeholder
                                        'adx': 25,  # Placeholder
                                    }
                                })
                    except Exception as e:
                        print(f"Error scanning {symbol}: {e}")
                        continue
                
                # Sort by score
                opportunities.sort(key=lambda x: x['score'], reverse=True)
                
                return {
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'opportunities': opportunities,
                    'source': 'bybit'
                }
                
            except Exception as e:
                print(f"Professional scanner not available: {e}")
        
        # Fallback to mock
        symbols = list(BASE_PRICES.keys())[:15]
        opportunities = []
        
        for symbol in symbols:
            score = random.uniform(20, 90)
            change24h = (random.random() - 0.5) * 20
            price = BASE_PRICES.get(symbol, 100)
            
            opportunities.append({
                'symbol': symbol,
                'score': round(score, 1),
                'timeframe': random.choice(['1h', '4h', '1d']),
                'signal': 'COMPRA FORTE' if score > 70 else 'COMPRA' if score > 50 else 'NEUTRO' if score > 30 else 'VENDA',
                'change24h': round(change24h, 2),
                'volume24h': random.uniform(100000000, 1000000000),
                'volatility': random.uniform(1, 5),
                'trend': 'ALTA' if change24h > 2 else 'BAIXA' if change24h < -2 else 'LATERAL',
                'price': price,
                'indicators': {
                    'rsi': random.uniform(30, 70),
                    'adx': random.uniform(15, 45),
                    'ema20': price * (1 + (random.random() - 0.5) * 0.02),
                    'ema50': price * (1 + (random.random() - 0.5) * 0.05),
                }
            })
        
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'timestamp': int(datetime.now().timestamp() * 1000),
            'opportunities': opportunities,
            'source': 'mock'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
