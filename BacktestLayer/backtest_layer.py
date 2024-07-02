import websockets
import asyncio
import csv
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from Common.decorators import backoff_reconnect
from typing import Dict, List
import os
import sys

class NotImplemented(Exception):
    pass

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

class Tick:
    def __init__(self, data: Dict):
        # regulating all dates across backtest-layer to be timezone naive
        self.ts_event = datetime.fromisoformat(data['ts_event'].replace('Z', '+00:00')).replace(tzinfo=None)
        self.rtype = data['rtype']
        self.publisher_id = data['publisher_id']
        self.instrument_id = data['instrument_id']
        self.open = float(data['open'])
        self.high = float(data['high'])
        self.low = float(data['low'])
        self.close = float(data['close'])
        self.volume = int(data['volume'])
        self.symbol = data['symbol']

class TickGenerator:
    # will only generate ticks from during trading hours
    #  - can adjust market_open, market_close to change this in the future
    def __init__(self, file_path, start_date, market_open, market_close):
        self.file_path = file_path
        self.start_date = start_date
        self.market_open = market_open
        self.market_close = market_close

    def __iter__(self):
        with open(self.file_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                data = dict(zip(headers, row))
                tick = Tick(data)
                # filter out afterhours and premarket trading
                if tick.ts_event >= self.start_date and self.market_open <= tick.ts_event.time() < self.market_close:
                    yield tick

class TickAggregator:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.ticks = {symbol: [] for symbol in symbols}
        self.last_known_values = {symbol: None for symbol in symbols}
    
    def add_tick(self, tick) -> None:
        self.ticks[tick.symbol].append(tick)

    def aggregate_period(self) -> Dict:
        # no aggregation logic
        aggregated_data = self.ticks.copy()

        # clear data for the period and update last know value for symbol
        #  - can use last_known_value to fill gaps if we dont see any ticks during the interval
        for symbol in self.symbols:
            if self.ticks[symbol]:
                self.last_known_values[symbol] = self.ticks[symbol][-1]
            self.ticks[symbol] = []

        # after clearing ticks return aggregated data
        return aggregated_data
    
    # pretty print for debugging
    def print_aggregated_data(self, aggregated_data) -> None:
        print("\nData this period:")
        for symbol in self.symbols:
            print(f"\tprocessed {len(aggregated_data[symbol])} ticks of {symbol} this period")

class BacktestStreamer:
    
    def __init__(self, model_ws_url, data_file_path, start_date, interval, market_open, market_close, symbols):
        self.data_generator = TickGenerator(data_file_path, start_date, time.fromisoformat(market_open), time.fromisoformat(market_close))
        self.aggregator = TickAggregator(symbols)
        self.model_ws_url = model_ws_url
        self.market_open = market_open
        self.start_of_period = None
        self.interval = interval
        self.symbols = symbols

        # testing fields
        self.periods_in_day = 0


    # returns a start datetime that matches 'market_open' on the same date as some Tick object
    def initalize_period(self, ts_event: datetime) -> datetime:
        return datetime.combine(ts_event.date(), time.fromisoformat(self.market_open))

    # if we cross over to a new day, OR the time on the next tick exceds the length of the interval
    def entering_new_period(self, ts_event: datetime) -> bool:
        return ts_event.date() != self.start_of_period.date() or (ts_event - self.start_of_period).total_seconds() >= self.interval

    # no decorator during testing, not connecting to other websockets yet
    # @backoff_reconnect()
    async def stream_data(self):
        for tick in self.data_generator:
            if not self.start_of_period:
                self.start_of_period = self.initalize_period(tick.ts_event)

            if self.entering_new_period(tick.ts_event):

                self.periods_in_day += 1
                if any(self.aggregator.ticks.values()):
                    aggregated_data = self.aggregator.aggregate_period()
                    self.aggregator.print_aggregated_data(aggregated_data)

                    # not implementing cross-layer websockets for backtesting yet
                    # await websocket.send(json.dumps(aggregated_data))

                if tick.ts_event.date() != self.start_of_period.date():
                    self.start_of_period = self.initalize_period(tick.ts_event)
                    
                    # visualization during testing
                    print(f"\n\nStarting New Day: {self.start_of_period.date()}  Ticks Today: {self.periods_in_day}")
                    print('-------------------------------')
                          
                    self.periods_in_day = 0
                else:
                    self.start_of_period += timedelta(seconds=self.interval)
            else:
                self.aggregator.add_tick(tick)

        if any(self.aggregator.ticks.values()):
            aggregated_data = self.aggregator.aggregate_period()
            # await websocket.send(json.dumps(aggregated_data))
            # print(f'Sent aggregated data:\n {aggregated_data}\n')

async def run_backtest():
    pass

async def main():
    print("Starting Backtest Layer websocket server on localhost:8003")
    backtest_websocket_server = websockets.serve(run_backtest, 'localhost', 8003)
    await backtest_websocket_server

    backtest_streamer = BacktestStreamer(
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