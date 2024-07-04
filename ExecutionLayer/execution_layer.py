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

class OrderException(Exception):
    pass

'''
Assuming shape of input JSON:
{
  position: 'BUY'|'SELL'|'NOOP',
  volume: int,
  ticker: string,
  orderType: 'MARKET'|'LIMIT'|'STOP'|'STOPLIMIT'
  limitPrice: float,
  stopPrice: float
}
'''

async def validate_and_create_order(signal_data: dict):
    
    position = signal_data.get('position', 'NOOP')
    if position == 'NOOP':
        return None

    if not (volume := signal_data.get('volume')):
        raise OrderException("Volume required to place order")

    limitPrice = signal_data.get('limitPrice')
    stopPrice = signal_data.get('stopPrice')
    orderType = signal_data.get('orderType')

    match orderType:
        case 'MARKET':
            return MarketOrder(position, volume)
        case 'LIMIT':
            if not limitPrice:
                raise OrderException("Limit price required for LIMIT order")
            return LimitOrder(position, volume, limitPrice)
        case 'STOP':
            if not stopPrice:
                raise OrderException("Stop price required for STOP order")
            return StopOrder(position, volume, stopPrice)
        case 'STOPLIMIT':
            if not stopPrice or not limitPrice:
                raise OrderException("Stop price AND limit price required for STOPLIMIT order")
            return StopLimitOrder(position, volume, limitPrice, stopPrice)
        case _:
            raise OrderException("Invalid order type provided")

async def place_order(signal_data: dict, gateway: IB):
    # the contract will remain the same regardless of the order type
    # order type is dependent on the orderType keyword
    try:
        order = await validate_and_create_order(signal_data)
        if order is None:
            return ("No trade was placed this period (NOOP)", None, None)
        
        contract = Stock(signal_data['ticker'], 'SMART', 'USD')
        # gateway.placeOrder(contract, order) 
        return ("Trade placed successfully", contract, order)
    except OrderException as e:
        return (f"Trade failed to process {e}", None, None)

async def handle_signal_stream(websocket, path, gateway: IB):
    print("Model client connected")
    async for signal in websocket:
        signal_data = json.loads(signal)
        print(f"Recieved JSON Signal\n{signal_data}")
        message, placed_contract, placed_order = await place_order(signal_data, gateway)
        print(f"Submitted Trade:\n - {placed_contract}\n - {placed_order}\n")

async def start_exe_ws_server(ib_gateway: IB):
    print("Starting execution WebSocket server on localhost:8002")
    execution_ws_server = websockets.serve(
        partial(handle_signal_stream, gateway=ib_gateway),
        "localhost", 8002
    )
    await execution_ws_server
    print("WebSocket server started")
    await asyncio.Future()
    
async def main():
    IB_CONNECTION_ON=True
    ib = IB()
    if IB_CONNECTION_ON:
        print("Connecting to IB Gateway")
        try:
            ib.connect('127.0.0.1', 7497, clientId=1)
        except Exception as e:
            print(f"IB Connection Failed: {e}")
        else:
            # ib.placeOrder(Stock('PLTR', 'SMART', 'USD'), MarketOrder('BUY', 100))
            ib.run(start_exe_ws_server(ib))
    else:
        await start_exe_ws_server(ib)

if __name__ == '__main__':
    asyncio.run(main())