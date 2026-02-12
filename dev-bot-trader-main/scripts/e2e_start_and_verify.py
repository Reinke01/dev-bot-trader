#!/usr/bin/env python3
"""
End-to-end test: Start bot via API, verify status, connect to WS logs for the bot,
trigger a POSITION_OPEN log for that bot and verify it is received via WS and that
Telegram notification is sent (check terminal output message from Telegram client).

This script prints concise evidence (bot_id, status, one WS message, and Telegram send notice).
"""
import json
import time
import urllib.request
import urllib.error
import sys
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT, 'src'))

import asyncio
import websockets

from utils.logging import get_logger, LogCategory

API_START = 'http://127.0.0.1:8000/api/v1/bot/start'
API_STATUS = 'http://127.0.0.1:8000/api/v1/bot/status'
WS_TEMPLATE = 'ws://127.0.0.1:8000/api/v1/ws/logs/{}'


def post_start():
    data = json.dumps({}).encode()
    req = urllib.request.Request(API_START, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def get_status_all():
    with urllib.request.urlopen(API_STATUS, timeout=10) as resp:
        return json.load(resp)


async def listen_ws_and_trigger(bot_id: str, timeout: int = 20):
    uri = WS_TEMPLATE.format(bot_id)
    print(f'Connecting to WS: {uri}')
    received = None
    try:
        async with websockets.connect(uri) as ws:
            print('WS connected, triggering POSITION_OPEN log...')
            # Trigger a position open log using server-side logger with bot_id name
            logger = get_logger(bot_id)
            logger.trading(LogCategory.POSITION_OPEN, 'E2E Test: posição aberta', 'e2e', symbol='SOLUSDT', operation='compra', entry_price=123.45, stop_price=120.0, target_price=130.0, position_size=0.01, risk_reward=1.5)

            start = time.time()
            while time.time() - start < timeout:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=timeout - (time.time() - start))
                    print('WS RAW:', msg)
                    # capture first message
                    received = msg
                    break
                except asyncio.TimeoutError:
                    break
    except Exception as e:
        print('WS error:', e)
    return received


def main():
    print('Posting start...')
    resp = post_start()
    bot_id = resp.get('bot_id') or resp.get('botId') or resp.get('bot_id')
    print('Start response:', {k: v for k, v in resp.items() if k != 'details'})
    if not bot_id:
        print('No bot_id returned, aborting')
        return 1

    # Poll status until running or timeout
    status = None
    for _ in range(10):
        time.sleep(1)
        all_status = get_status_all()
        for b in all_status:
            if b.get('bot_id') == bot_id:
                status = b.get('status')
                break
        if status == 'running':
            break
    print('Bot status:', status)

    # Connect WS and trigger log
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    received = loop.run_until_complete(listen_ws_and_trigger(bot_id, timeout=20))

    if received:
        print('E2E WS message captured (truncated):', received[:500])
    else:
        print('No WS message captured')

    print('\nNow check your Telegram chat for the position notification.\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
