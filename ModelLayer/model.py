import random
import json

def model(data):
    fake_decisions = [
        {'position': 'BUY', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'MARKET'},
        {'position': 'SELL', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'MARKET'},
        {'position': 'BUY', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'LIMIT', 'limitPrice': round(random.uniform(24, 26), 2)},
        {'position': 'SELL', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'LIMIT', 'limitPrice': round(random.uniform(24, 26), 2)},
        {'position': 'BUY', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'STOP', 'stopPrice': round(random.uniform(24.5, 25.5), 2)},
        {'position': 'SELL', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'STOP', 'stopPrice': round(random.uniform(24.5, 25.5), 2)},
        {'position': 'BUY', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'STOPLIMIT', 'limitPrice': round(random.uniform(25, 26), 2), 'stopPrice': round(random.uniform(24, 25), 2)},
        {'position': 'SELL', 'volume': random.randint(1, 10), 'ticker': 'PLTR', 'orderType': 'STOPLIMIT', 'limitPrice': round(random.uniform(25, 26), 2), 'stopPrice': round(random.uniform(24, 25), 2)},
        {'position': 'NOOP'}
    ]
    random_signal = random.choice(fake_decisions)
    signal_json = json.dumps(dict(random_signal))
    return signal_json