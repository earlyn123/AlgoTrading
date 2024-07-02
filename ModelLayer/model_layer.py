import asyncio
import websockets
from .model import model
from Common.websocket_helpers import send_socket_message
from Common.decorators import backoff_reconnect
import sys
import os

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

EXE_SOCKET_URL = "ws://localhost:8002"

signal_counter = 0

@backoff_reconnect()
async def generate_signal(execution_ws, websocket, path):
    global signal_counter
    async for data in websocket:
        signal_counter += 1
        print(f"Recieved Signal #{signal_counter}")
        trading_signal = model(data)
        await send_socket_message(trading_signal, execution_ws)
        print(f"Sent signal {trading_signal}")

async def main():
    
    async def handler(websocket, path):
        await generate_signal(EXE_SOCKET_URL, websocket, path)

    print("Starting model WebSocket server on localhost:8001")
    model_layer_ws = websockets.serve(handler, 'localhost', 8001)
    await model_layer_ws
    await asyncio.Future() 

if __name__ == '__main__':
    asyncio.run(main())