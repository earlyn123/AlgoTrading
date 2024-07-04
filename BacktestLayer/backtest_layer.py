import websockets
import asyncio
from datetime import datetime
from Common.decorators import backoff_reconnect
from backtest_data_stream import StreamingEngine
import os
import sys

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

async def run_backtest():
    pass

async def main():
    print("Starting Backtest Layer websocket server on localhost:8003")
    backtest_websocket_server = websockets.serve(run_backtest, 'localhost', 8003)
    await backtest_websocket_server

    backtest_streamer = StreamingEngine(
        model_ws_url='ws://localhost:8001', # backtesting layer streams data to model layer
        data_file_path=r'./BacktestLayer/data/nasdaq_stocks_last_year.csv',
        start_date=datetime(2023, 7, 1),
        interval=60,  # measured in seconds
        market_open='13:30',
        market_close='20:00',
        # symbols that exist in input dataset
        symbols=['TSLA', 'LCID', 'F', 'GM', 'RIVN', 'QQQ']
    )

    # on a separate thread start streaming data
    asyncio.create_task(backtest_streamer.stream_data())

    await asyncio.Future()  # run event loop forever

if __name__ == '__main__':
    asyncio.run(main())