"""
generator will subscribe to a websocket that lives in the backtest_engine
each time the generator produces a tick it will send that tick information to the backtest_engine
the engine will store that tick data in a dictionary 

signals will also be sent to the backetst_engine via a different websocket
as we recieve signals we look up price data in the dictionary
once the signal is recieved we can delete all price data from before that time-stamp from our dictionary to save memory

use the current price 1 second after the signal is recieved to place market order

Tasks for BacktestEngine: 
[x] Initialization 
    [x] Bankroll
    [x] Start date
    [x] Period length (for pnl calculation)

[ ] Websockets
    [x] On rceive tick data
        [x] Store tick data for price lookup
    [ ] On receive signal data
        [ ] Place order

[ ] Placing orders
    [ ] Parse signal data from websocket
    [ ] Retrieve tick data at a certain timestamp
    [ ] Clear tick data behind signal timestamp (so memory doesnt explode)
    [ ] Place market order
    [ ] Calculate PNL
    [ ] Log PNL from each period

[x] Entrypoint
    [x] Start tick socket server
    [x] Start signal socket server
"""
import asyncio
import websockets
from sortedcontainers import SortedDict
from datetime import datetime, timedelta
from typing import Dict
from BacktestLayer.tick import Tick
import pickle
from Common.exceptions import IncorrectObjectType
import logging

TICK_PRICE_WS_PORT=8005
SIGNAL_INFO_WS_PORT=8006

SymbolPriceLookup = Dict[str, SortedDict[datetime, Tick]]

def retrieve_most_recent_tick(price_history: SortedDict[datetime, Tick], query_time: datetime):
    if query_time in price_history:
        return price_history[query_time]
    
    index = price_history.bisect_left(query_time)

    # this means there is no historical price data for the instrument
    if index == 0:
        return None
    
    nearest_prior_tick = price_history.iloc[index-1]
    return price_history[nearest_prior_tick]

class BacktestEngine():
    
    def __init__(self, bankroll: float, start_date: datetime, period_length: timedelta, trading_symbol: str):
        self.bankroll = bankroll
        self.start_date = start_date
        self.period_length = period_length
        self.trading_symbol = trading_symbol

        self.price_history: SymbolPriceLookup = {}
        self.pnl: Dict[datetime, float] = {}
        self.period_number = 0

    def display_price_history(self, symbol=None):
        if not symbol:
            symbol = self.trading_symbol
        
        historical_symbol_prices = self.price_history.get(symbol)
        if not historical_symbol_prices:
            return
        
        logging.info(f"\n\nPrice history for: {symbol}")
        for key,value in historical_symbol_prices.items():
            logging.info(f"Historical price at {key} -> {value.close}")

    async def handle_ticks(self, websocket):
        # will arrive as a pickle bytestream, need to unpack and extract timestamp
        # need to unpack and store in self.price_history
        async for tick in websocket:
            try:
                tick_obj: Tick = pickle.loads(tick)
                if type(tick_obj) != Tick:
                    raise IncorrectObjectType(type(tick_obj))
            except IncorrectObjectType as e:
                logging.error(f"Expexted type 'Tick' recieved: {e}")
            else:
                # only need to track ticks for instruments we are trading
                symbol = tick_obj.symbol
                if symbol != self.trading_symbol:
                    continue

                timestamp = tick_obj.ts_event
                if not self.price_history.get(symbol):
                    self.price_history[symbol] = SortedDict()

                self.price_history[symbol][timestamp] = tick_obj
            
            # self.display_price_history()
            
    def handle_signals(self, websocket):
        pass

    async def run(self):
        # need to serve to endpoints
            # price data
            # signal data
        logging.info(f"Starting rec_tick and rec_signal websocket servers on ports {TICK_PRICE_WS_PORT} and {SIGNAL_INFO_WS_PORT}")
        rec_tick_ws   = websockets.serve(self.handle_ticks, 'localhost', TICK_PRICE_WS_PORT)
        rec_signal_ws = websockets.serve(self.handle_signals, 'localhost', SIGNAL_INFO_WS_PORT)
        await asyncio.gather(rec_signal_ws, rec_tick_ws)
        logging.info("rec_tick and rec_signal websocket servers started")