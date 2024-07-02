import websockets
import asyncio
import csv
from datetime import datetime, timedelta, time
from common.decorators import backoff_reconnect
import os
import sys

class NotImplemented(Exception):
    pass

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

MODEL_SOCKET_URL = 'ws://localhost:8001'
DATA_FILE_PATH = r'./BacktestLayer/data/nasdaq_stocks_last_year.csv'
SIGNAL_INTERVAL = 60  # measured in seconds
MARKET_OPEN = '13:30'
MARKET_CLOSE = '20:00'
SYMBOLS = ['TSLA', 'LCID', 'F', 'GM', 'RIVN', 'QQQ']
START_DATE = datetime(2022, 7, 1)

def create_tick_data_generator(file_path, start_date):
    market_open_time = time.fromisoformat(MARKET_OPEN)
    market_close_time = time.fromisoformat(MARKET_CLOSE)
    
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            tick = dict(zip(headers, row))
            tick_time = datetime.fromisoformat(tick['ts_event'].replace('Z', '+00:00')).replace(tzinfo=None)
            # generator should only produce ticks during market hours
            if tick_time >= start_date and market_open_time <= tick_time.time() < market_close_time:
                yield tick

def aggregate_period(ticks_per_symbol, last_known_values):
    return ticks_per_symbol

def print_symbol_dict(symbol_data):
    print("\nData this period:")
    for symbol in SYMBOLS:
        print(f"\tprocessed {len(symbol_data[symbol])} ticks of {symbol} this period")

# @backoff_reconnect()
async def stream_data_to_model(model_ws: websockets.WebSocketClientProtocol, interval: int):
    tick_data_generator = create_tick_data_generator(DATA_FILE_PATH, START_DATE)
    
    start_of_period = None
    periods_in_day = 0  # FOR TESTING
    ticks = {symbol: [] for symbol in SYMBOLS}
    last_known_values = {symbol: None for symbol in SYMBOLS}

    for tick in tick_data_generator:
        tick_time = datetime.fromisoformat(tick['ts_event'].replace('Z', '+00:00')).replace(tzinfo=None)

        if not start_of_period:
            start_of_period = datetime.combine(tick_time.date(), time.fromisoformat(MARKET_OPEN))

        symbol = tick['symbol']
        # if the trade we are currently reading is outside the desired period
        #  - aggregate the trades from the previous period
        if tick_time.date() != start_of_period.date() or (tick_time - start_of_period).total_seconds() >= interval:
            periods_in_day += 1
            if any(ticks.values()):
                aggregated_data = aggregate_period(ticks, last_known_values)
                print_symbol_dict(aggregated_data)
                # print(f'Sent aggregated data:\n {aggregated_data}\n')

            for symbol in SYMBOLS:
                if ticks[symbol]:
                    last_known_values[symbol] = ticks[symbol][-1]
                ticks[symbol] = []

            if tick_time.date() != start_of_period.date():
                # Reset start_of_period to MARKET_OPEN on the new day
                start_of_period = datetime.combine(tick_time.date(), time.fromisoformat(MARKET_OPEN))
                print(f"\n\nStarting New Day: {start_of_period.date()}  Ticks Today: {periods_in_day}\n---------------------------------------------------")

                periods_in_day = 0  # FOR TESTING
            else:
                start_of_period += timedelta(seconds=interval)
        else:
            # print(f"Tick Time: {tick_time} \nStart of period: {start_of_period}")
            # print(f"Remaining time in interval: {(interval - (tick_time - start_of_period).total_seconds())}\n")
            ticks[symbol].append(tick)

    # cleanup for EOF
    if any(ticks.values()):
        aggregated_data = aggregate_period(ticks, last_known_values)
        # Send aggregated_data to websocket
        # await websocket.send(json.dumps(aggregated_data))
        # print(f'Sent aggregated data:\n {aggregated_data}\n')

async def run_backtest(websocket: websockets.WebSocketServerProtocol):
    # receive data from the execution layer
    for message in websocket:
        pass
    return

async def main():
    print("Starting Backtest Layer websocket server on localhost:8003")

    # this takes data from the execution layer
    # backtest_layer_ws = websockets.serve(run_backtest, 'localhost', 8003)
    # await backtest_layer_ws
    # this sends data to the model layer
    # asyncio.create_task(stream_data_to_model(MODEL_SOCKET_URL))
    await stream_data_to_model(MODEL_SOCKET_URL, SIGNAL_INTERVAL)
    # await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
