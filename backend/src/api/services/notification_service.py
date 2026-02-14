import httpx
from utils.logging import get_logger, LogCategory

logger = get_logger("NotificationService")

async def send_webhook_notification(webhook_url: str, message: str, data: dict = None):
    """
    Sends a notification to a webhook URL (Zapier, Make, etc.)
    """
    if not webhook_url:
        logger.warning(LogCategory.SYSTEM, "Webhook URL não configurada. Notificação ignorada.")
        return False

    payload = {
        "message": message,
        "timestamp": data.get("last_update") if data else None,
        "symbol": data.get("symbol") if data else None,
        "score": data.get("score") if data else None,
        "rsi": data.get("rsi") if data else None,
        "details": data
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10.0)
            
            if response.status_code in [200, 201, 204]:
                logger.info(LogCategory.SYSTEM, f"✅ Notificação enviada com sucesso para: {webhook_url}")
                return True
            else:
                logger.error(LogCategory.SYSTEM, f"❌ Erro ao enviar webhook: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"❌ Exceção ao enviar webhook: {str(e)}")
        return False

async def notify_high_score_signal(webhook_url: str, result: dict):
    """
    Convenience function to notify specifically about high score signals.
    """
    symbol = result.get("symbol")
    score = result.get("score")
    rsi = result.get("rsi")
    
    msg = f"🚀 SINAL EXPLOSIVO: {symbol} atingiu Score {score}/5! RSI em {rsi}. Verifique o Terminal agora!"
    
    return await send_webhook_notification(webhook_url, msg, result)
