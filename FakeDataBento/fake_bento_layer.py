import websockets
import asyncio
import json
import pandas as pd
from common.websocket_helpers import send_socket_message
import sys
import os

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)


SOCKET_URL = "ws://localhost:8000"

async def main():
    data = pd.read_csv("FakeDataBento/one_day_google.csv")

    # just to simulate live data coming in for dev purposes
    async def stream(data, msg_frequency):
        interval = 1.0 / msg_frequency
        async with websockets.connect(SOCKET_URL) as data_ws:
            for index, row in data.iterrows():
                trade_data = row.to_dict()
                trade_data_json = json.dumps(trade_data)
        
                await send_socket_message(trade_data_json, data_ws)
        
                print(f"\nSent message #{index + 1}")
                print(trade_data_json)
        
                await asyncio.sleep(interval)

    await stream(data, 2)

if __name__ == '__main__':
    main()