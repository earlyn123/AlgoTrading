"""
generator will subscribe to a websocket that lives in the backtest_engine
each time the generator produces a tick it will send that tick information to the backtest_engine
the engine will store that tick data in a dictionary 

signals will also be sent to the backetst_engine via a different websocket
as we recieve signals we look up price data in the dictionary
once the signal is recieved we can delete all price data from before that time-stamp from our dictionary to save memory

use the current price 1 second after the signal is recieved to place market order

Tasks for BacktestEngine: 
[ ] Initialization 
    [ ] Bankroll
    [ ] Start date
    [ ] Period length (for pnl calculation)

[ ] Websockets
    [ ] On rceive tick data
        [ ] Store tick data for price lookup
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
from datetime import datetime, timedelta
from typing import Dict

TICK_PRICE_WS_PORT=8005
SIGNAL_INFO_WS_PORT=8006


class BacktestEngine():
    
    def __init__(self, bankroll: float, start_date: datetime, period_length: timedelta):
        self.bankroll = bankroll
        self.start_date = start_date
        self.period_length = period_length

        self.price_history: Dict[datetime, float] = {}
        self.pnl: Dict[datetime, float] = {}
        self.period_number = 0

    def handle_ticks(self, websocket):
        pass

    def handle_signals(self, websocket):
        pass

    async def run(self):
        # need to serve to endpoints
            # price data
            # signal data
        rec_tick_ws   = websockets.serve(self.handle_ticks, 'loclahost', TICK_PRICE_WS_PORT)
        rec_signal_ws = websockets.serve(self.handle_signals, 'localhost', SIGNAL_INFO_WS_PORT)
        await asyncio.gather(rec_signal_ws, rec_tick_ws)




