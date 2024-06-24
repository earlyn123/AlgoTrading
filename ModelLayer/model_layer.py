# TODO
# WS server to accept clean and aggegated 10 second chunks lives here
# call the model to get the predicted signals
# pass signals to the Execution Layer
# Will act as a WS client for the Execution Layer WS server 
import asyncio
import websockets
from .model import model
from common.websocket_helpers import send_socket_message
from common.decorators import backoff_reconnect

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