import asyncio
import websockets
from .aggregate import aggregate_trades
from .clean import clean_chunk
from common.websocket_helpers import send_socket_message
from common.decorators import backoff_reconnect
import json

SIGNAL_FREQUENCY = 10
MODEL_SOCKET_URL = "ws://localhost:8001"

trade_queue = asyncio.Queue()

async def incoming_data_stream(websocket, path):
    print("data streaming client connected")
    async for message in websocket:
        await trade_queue.put(message)

@backoff_reconnect()
async def process_trades(model_ws):
    global trade_queue

    while True:
        trades = []
        while not trade_queue.empty():
            trade = await trade_queue.get()
            trades.append(trade)
        if trades:
            clean_data = clean_chunk(trades)
            aggregated_data = aggregate_trades(clean_data)
            print(f"aggregated {aggregated_data} trades")

            aggregated_data_json = json.dumps(aggregated_data)
            await send_socket_message(aggregated_data_json, model_ws)
        else:
            print(f"No trades came during this {SIGNAL_FREQUENCY} second window")

        await asyncio.sleep(SIGNAL_FREQUENCY)

async def main():
    print("Starting data WebSocket server on localhost:8001")
    start_ws_server = websockets.serve(incoming_data_stream, "localhost", 8000)
    await start_ws_server

    processing_task = asyncio.create_task(process_trades(MODEL_SOCKET_URL))
    
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
