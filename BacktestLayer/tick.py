from typing import Dict
from datetime import datetime

class Tick:
    def __init__(self, data: Dict):
        # regulating all dates across backtest-layer to be timezone naive
        self.ts_event = datetime.fromisoformat(data['ts_event'].replace('Z', '+00:00')).replace(tzinfo=None)
        self.rtype = data['rtype']
        self.publisher_id = data['publisher_id']
        self.instrument_id = data['instrument_id']
        self.open = float(data['open'])
        self.high = float(data['high'])
        self.low = float(data['low'])
        self.close = float(data['close'])
        self.volume = int(data['volume'])
        self.symbol = data['symbol']