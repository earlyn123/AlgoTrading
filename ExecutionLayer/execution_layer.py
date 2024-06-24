import asyncio
import websockets
from ib_insync import *
import json




'''
Assuming shape of input JSON:
{
  position: 'BUY'|'SELL'|'NOOP',
  volume: int,
  ticker: string
}

'''
async def post_trades(websocket, path):
    async for signal in websocket:
        signal_data = json.loads(signal)
        print(f"Recieved JSON Signal\n{signal_data}")

async def start_exe_ws_server():
    execution_ws_server = websockets.serve(post_trades, "localhost", 8002)
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
        ib.run(start_exe_ws_server())

if __name__ == '__main__':
    asyncio.run(main())