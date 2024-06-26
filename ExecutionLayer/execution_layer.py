import asyncio
import websockets
from ib_insync import *
import json
import sys
import os
import nest_asyncio
from functools import partial

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

nest_asyncio.apply()

'''
Assuming shape of input JSON:
{
  position: 'BUY'|'SELL'|'NOOP',
  volume: int,
  ticker: string
}
'''

async def place_order(position: str, volume: int, ticker: str, gateway: IB):
    if position == 'NOOP':
        return ("No trade was placed this period (NOOP)",None, None)
    contract = Stock(ticker, 'SMART', 'USD')
    order = MarketOrder(position, volume)
    # uncomment below to actually place the trade in TWS
    # gateway.placeOrder(contract, order)
    return ("Placed a trade", contract, order)

async def handle_signal_stream(websocket, path, gateway: IB):
    async for signal in websocket:
        signal_data = json.loads(signal)
        print(f"Recieved JSON Signal\n{signal_data}")
        position: str = signal_data['position'].upper()
        if position != 'NOOP':
            volume: int = signal_data['volume']
            ticker: str = signal_data['ticker'].upper()
        else:
            volume = 0
            ticker = ''
        message, placed_contract, placed_order = await place_order(position, volume, ticker, gateway)
        print(f"Submitted Trade:\n - {placed_contract}\n - {placed_order}\n")


async def start_exe_ws_server(ib_gateway: IB):
    execution_ws_server = websockets.serve(
        partial(handle_signal_stream, gateway=ib_gateway),
        "localhost", 8002
    )
    await execution_ws_server
    await asyncio.Future()
    

async def main():
    print("Connecting to IB Gateway")
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7497, clientId=1)
    except Exception as e:
        print(f"IB Connection Failed: {e}")
    else:
        print("Starting execution WebSocket server on localhost:8002")
        # ib.placeOrder(Stock('PLTR', 'SMART', 'USD'), MarketOrder('BUY', 100))
        ib.run(start_exe_ws_server(ib))

if __name__ == '__main__':
    asyncio.run(main())