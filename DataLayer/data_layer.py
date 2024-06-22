import asyncio
import websockets
from aggregate import aggregate_trades
from clean import clean_chunk

trade_queue = asyncio.Queue()

SIGNAL_FREQUENCY = 5

async def incoming_data_stream(websocket, path):
    print("data streaming client connected")
    async for message in websocket:
        await trade_queue.put(message)
        # print(f"Received message #{trade_queue.qsize()}")

async def process_trades():
    global trade_queue
    while True:
        await asyncio.sleep(SIGNAL_FREQUENCY)
        trades = []
        while not trade_queue.empty():
            trade = await trade_queue.get()
            trades.append(trade)
        
        if trades:
            clean_data = clean_chunk(trades)
            aggregated_data = aggregate_trades(clean_data)
            print(f"aggregated {aggregated_data} trades")

            # TODO
            # send the aggregation over to the model layer's WS server here
        else:
            print(f"no trades came during this {SIGNAL_FREQUENCY} second window")

async def main():
    start_ws_server = websockets.serve(incoming_data_stream, "localhost", 8000)
    await start_ws_server

    asyncio.create_task(process_trades())

    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
