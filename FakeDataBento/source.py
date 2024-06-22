import websockets
import asyncio
import json
import pandas as pd

data = pd.read_csv("one_day_google.csv")
socket_url = "ws://localhost:8000"


# just to simulate live data coming in for dev purposes
async def stream(data, msg_frequency):
    interval = 1.0 / msg_frequency
    async with websockets.connect(socket_url) as ws:
        for index, row in data.iterrows():
            trade_data = row.to_dict()
            trade_data_json = json.dumps(trade_data)
    
            await ws.send(trade_data_json)
    
            print(f"Sent message #{index + 1}")
    
            await asyncio.sleep(interval)

asyncio.run(stream(data, 10))
