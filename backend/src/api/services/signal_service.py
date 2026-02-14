import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.logging import get_logger, LogCategory

class SignalService:
    def __init__(self):
        self._signals: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self.logger = get_logger("SignalService")

    def update_signals(self, scanner_results: List[Dict[str, Any]]):
        """
        Updates the list of top signals based on scanner results.
        Only keeps high-score signals (score >= 4).
        """
        with self._lock:
            # Filter for high scores and take top 10
            high_scores = [res for res in scanner_results if res.get('score', 0) >= 4]
            # Sort by score descending
            high_scores = sorted(high_scores, key=lambda x: x['score'], reverse=True)[:10]
            
            # Map to signal format
            self._signals = high_scores
            self.logger.debug(LogCategory.SYSTEM, f"Updated signal feed: {len(self._signals)} high-score assets found.")

    def get_signals(self) -> List[Dict[str, Any]]:
        with self._lock:
            return self._signals

    def get_signal_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            for signal in self._signals:
                if signal['symbol'] == symbol:
                    return signal
            return None

_signal_service_instance = None

def get_signal_service() -> SignalService:
    global _signal_service_instance
    if _signal_service_instance is None:
        _signal_service_instance = SignalService()
    return _signal_service_instance
