import websockets
import asyncio
from datetime import datetime, timedelta
from Common.decorators import backoff_reconnect
from BacktestLayer.backtest_data_stream import StreamingEngine
from BacktestLayer.backtest_engine import BacktestEngine
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

async def run_backtest():
    pass

async def main():
    # print("Starting Backtest Layer websocket server on localhost:8003")
    # backtest_websocket_server = websockets.serve(run_backtest, 'localhost', 8003)
    # await backtest_websocket_server

    backtest_engine = BacktestEngine(
        bankroll=1000000.0,
        start_date=datetime(2023,7,1),
        period_length=timedelta(days=1),
        trading_symbol='RIVN'
    )

    MODEL_WS_URL='ws://localhost:8001'
    BACKTEST_WS_URL='ws://localhost:8005'
    backtest_streamer = StreamingEngine(
        model_ws_url=MODEL_WS_URL, # backtesting layer streams data to model layer
        backtest_ws_url=BACKTEST_WS_URL,
        data_file_path=r'./BacktestLayer/data/nasdaq_stocks_last_year.csv',
        start_date=datetime(2023, 7, 1),
        interval=60,  # measured in seconds
        market_open='13:30',
        market_close='20:00',
        # symbols that exist in input dataset
        symbols=['TSLA', 'LCID', 'F', 'GM', 'RIVN', 'QQQ']
    )

    # on a separate thread start streaming data
    backtest_task = asyncio.create_task(backtest_engine.run())
    streaming_task = asyncio.create_task(backtest_streamer.stream_data(MODEL_WS_URL, BACKTEST_WS_URL))
    await asyncio.gather(backtest_task, streaming_task)  # run event loop forever

if __name__ == '__main__':
    asyncio.run(main())