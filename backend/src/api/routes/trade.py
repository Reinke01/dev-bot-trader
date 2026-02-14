from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import random
import os

router = APIRouter()

# Check if live trading is enabled via environment variable
ENABLE_LIVE_TRADING = os.getenv('ENABLE_LIVE_TRADING', 'false').lower() == 'true'


class OrderRequest(BaseModel):
    symbol: str
    side: str  # 'buy' or 'sell'
    type: str  # 'market', 'limit', 'stop', 'stop_limit'
    quantity: float
    price: Optional[float] = None
    stopPrice: Optional[float] = None
    leverage: Optional[int] = 1
    stopLoss: Optional[float] = None
    takeProfit: Optional[float] = None
    mode: str = 'paper'  # 'paper' or 'live'


# In-memory storage for mock orders and positions
mock_orders: List[Dict] = []
mock_positions: List[Dict] = []


def generate_order_id() -> str:
    """Generate a unique order ID"""
    timestamp = int(datetime.now().timestamp() * 1000)
    random_part = random.randint(1000, 9999)
    return f"ORD-{timestamp}-{random_part}"


def generate_position_id(symbol: str) -> str:
    """Generate a unique position ID"""
    timestamp = int(datetime.now().timestamp() * 1000)
    return f"POS-{symbol}-{timestamp}"


@router.post('/trade/execute')
async def execute_trade(order: OrderRequest):
    """
    Execute a trade order.
    
    Supports both paper trading (simulation) and live trading (if enabled).
    
    Paper mode: Creates simulated orders and positions
    Live mode: Requires ENABLE_LIVE_TRADING=true environment variable
    
    To integrate with real exchange:
    - Import your exchange client (Bybit, Binance, etc.)
    - Implement real order execution
    - Handle errors and response formatting
    - Implement proper risk management
    """
    try:
        # Validate mode
        if order.mode == 'live':
            if not ENABLE_LIVE_TRADING:
                return {
                    'success': False,
                    'message': '🔒 Trading ao vivo está desabilitado. Configure ENABLE_LIVE_TRADING=true no backend.',
                    'mode': 'live',
                    'timestamp': int(datetime.now().timestamp() * 1000),
                }
            
            # Additional confirmation for live trading
            return {
                'success': False,
                'message': '⚠️ Live trading não implementado. Por segurança, apenas Paper trading está disponível.',
                'mode': 'live',
                'timestamp': int(datetime.now().timestamp() * 1000),
            }
        
        # Paper trading simulation
        order_id = generate_order_id()
        timestamp = int(datetime.now().timestamp() * 1000)
        
        # Mock current price
        base_prices = {
            'BTCUSDT': 95000,
            'ETHUSDT': 2800,
            'SOLUSDT': 87,
            'BNBUSDT': 580,
            'XRPUSDT': 2.1,
            'ADAUSDT': 0.95,
            'DOGEUSDT': 0.28,
            'ARBUSDT': 0.75,
        }
        
        execution_price = order.price if order.price and order.type != 'market' else base_prices.get(order.symbol, 100)
        
        # Create order record
        order_record = {
            'id': order_id,
            'symbol': order.symbol,
            'side': order.side,
            'type': order.type,
            'status': 'filled',  # Instant fill in paper mode
            'quantity': order.quantity,
            'filledQuantity': order.quantity,
            'price': order.price,
            'avgPrice': execution_price,
            'timestamp': timestamp,
            'updatedAt': timestamp,
        }
        
        mock_orders.append(order_record)
        
        # Create position if it doesn't exist
        position_exists = False
        for pos in mock_positions:
            if pos['symbol'] == order.symbol:
                position_exists = True
                # Update existing position
                if order.side == pos['side']:
                    # Add to position
                    total_qty = pos['quantity'] + order.quantity
                    pos['entryPrice'] = ((pos['entryPrice'] * pos['quantity']) + (execution_price * order.quantity)) / total_qty
                    pos['quantity'] = total_qty
                else:
                    # Reduce or close position
                    pos['quantity'] -= order.quantity
                    if pos['quantity'] <= 0:
                        mock_positions.remove(pos)
                break
        
        if not position_exists and order.quantity > 0:
            # Create new position
            position_side = 'long' if order.side == 'buy' else 'short'
            position_id = generate_position_id(order.symbol)
            
            position_record = {
                'id': position_id,
                'symbol': order.symbol,
                'side': position_side,
                'quantity': order.quantity,
                'entryPrice': execution_price,
                'currentPrice': execution_price,
                'unrealizedPnl': 0,
                'unrealizedPnlPercent': 0,
                'leverage': order.leverage or 1,
                'liquidationPrice': execution_price * (0.9 if position_side == 'long' else 1.1),
                'timestamp': timestamp,
            }
            
            mock_positions.append(position_record)
        
        return {
            'success': True,
            'orderId': order_id,
            'message': f'✅ Ordem {order.side.upper()} executada com sucesso (PAPER TRADING)',
            'order': order_record,
            'mode': 'paper',
            'timestamp': timestamp,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order execution failed: {str(e)}")


@router.get('/trade/orders')
async def get_orders():
    """
    Get list of orders (both open and filled).
    
    Returns mock data. To integrate with real exchange:
    - Import your exchange client
    - Call client.get_orders()
    - Format response to match this structure
    """
    try:
        # Return last 20 orders
        orders = mock_orders[-20:] if mock_orders else []
        
        # If no mock orders, generate some sample ones
        if not orders:
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
            for i in range(5):
                timestamp = int(datetime.now().timestamp() * 1000) - (i * 60000)
                orders.append({
                    'id': f"ORD-{timestamp}-{random.randint(1000, 9999)}",
                    'symbol': random.choice(symbols),
                    'side': random.choice(['buy', 'sell']),
                    'type': random.choice(['market', 'limit']),
                    'status': random.choice(['open', 'filled', 'cancelled']),
                    'quantity': round(random.uniform(0.1, 10), 4),
                    'filledQuantity': round(random.uniform(0, 10), 4),
                    'price': round(random.uniform(50, 100000), 2),
                    'avgPrice': round(random.uniform(50, 100000), 2),
                    'timestamp': timestamp,
                    'updatedAt': timestamp,
                })
        
        return {
            'orders': orders,
            'count': len(orders),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/trade/positions')
async def get_positions():
    """
    Get list of open positions.
    
    Returns mock data. To integrate with real exchange:
    - Import your exchange client
    - Call client.get_positions()
    - Calculate PnL and format response
    """
    try:
        # Update current prices and PnL for mock positions
        base_prices = {
            'BTCUSDT': 95000,
            'ETHUSDT': 2800,
            'SOLUSDT': 87,
            'BNBUSDT': 580,
            'XRPUSDT': 2.1,
            'ADAUSDT': 0.95,
            'DOGEUSDT': 0.28,
            'ARBUSDT': 0.75,
        }
        
        for pos in mock_positions:
            current_price = base_prices.get(pos['symbol'], pos['entryPrice'])
            pos['currentPrice'] = current_price
            
            # Calculate PnL
            price_diff = current_price - pos['entryPrice']
            if pos['side'] == 'short':
                price_diff = -price_diff
            
            pos['unrealizedPnl'] = round(price_diff * pos['quantity'], 2)
            pos['unrealizedPnlPercent'] = round((price_diff / pos['entryPrice']) * 100, 2)
        
        positions = mock_positions if mock_positions else []
        
        # If no mock positions, generate some sample ones
        if not positions:
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
            for symbol in symbols[:2]:
                timestamp = int(datetime.now().timestamp() * 1000)
                entry_price = base_prices.get(symbol, 100)
                current_price = entry_price * random.uniform(0.95, 1.05)
                side = random.choice(['long', 'short'])
                quantity = round(random.uniform(0.1, 5), 4)
                
                price_diff = current_price - entry_price
                if side == 'short':
                    price_diff = -price_diff
                
                positions.append({
                    'id': f"POS-{symbol}-{timestamp}",
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'entryPrice': round(entry_price, 2),
                    'currentPrice': round(current_price, 2),
                    'unrealizedPnl': round(price_diff * quantity, 2),
                    'unrealizedPnlPercent': round((price_diff / entry_price) * 100, 2),
                    'leverage': random.randint(1, 10),
                    'liquidationPrice': round(entry_price * (0.9 if side == 'long' else 1.1), 2),
                    'timestamp': timestamp,
                })
        
        return {
            'positions': positions,
            'count': len(positions),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/trade/orders/{order_id}')
async def cancel_order(order_id: str):
    """
    Cancel an open order.
    
    Mock implementation. To integrate with real exchange:
    - Import your exchange client
    - Call client.cancel_order(order_id)
    """
    try:
        # Find and update order status
        for order in mock_orders:
            if order['id'] == order_id:
                order['status'] = 'cancelled'
                order['updatedAt'] = int(datetime.now().timestamp() * 1000)
                return {
                    'success': True,
                    'message': f'Order {order_id} cancelled',
                    'order': order,
                }
        
        return {
            'success': False,
            'message': f'Order {order_id} not found',
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/trade/close-position/{symbol}')
async def close_position(symbol: str):
    """
    Close a position (market order to opposite side).
    
    Mock implementation. To integrate with real exchange:
    - Import your exchange client
    - Get current position
    - Place market order on opposite side
    """
    try:
        # Find position
        position = None
        for pos in mock_positions:
            if pos['symbol'] == symbol:
                position = pos
                break
        
        if not position:
            return {
                'success': False,
                'message': f'Position for {symbol} not found',
            }
        
        # Remove position
        mock_positions.remove(position)
        
        return {
            'success': True,
            'message': f'Position {symbol} closed',
            'position': position,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
