import asyncio
import websockets
from .model import model
from Common.websocket_helpers import send_socket_message
from Common.decorators import backoff_reconnect
import sys
import os
import json

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

EXE_SOCKET_URL = "ws://localhost:8002"

signal_counter = 0

data_queue = asyncio.Queue()

async def handle_data_stream(websocket):
    print("Data Layer client connected")
    async for data in websocket:
        await data_queue.put(data)

@backoff_reconnect()
async def generate_signal(execution_ws):
    global signal_counter
    global data_queue

    while True:
        while not data_queue.empty():
            signal_counter += 1
            data = await data_queue.get()
            print(f"Recieved Signal #{signal_counter}")
            clean_aggregated_data = json.loads(data)
            trading_signal = model(clean_aggregated_data)
            await send_socket_message(trading_signal, execution_ws)
            print(f"Sent signal {trading_signal}")

async def main():

    print("Starting model WebSocket server on localhost:8001")
    model_layer_ws = websockets.serve(handle_data_stream, 'localhost', 8001)
    await model_layer_ws

    asyncio.create_task(generate_signal(EXE_SOCKET_URL))

    await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())