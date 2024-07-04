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

[ ] Entrypoint
    [ ] Start tick socket server
    [ ] Start signal socket server
"""
import asyncio
import websockets

class BacktestEngine():
    pass



