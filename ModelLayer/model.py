import random
import json

def model(data):
    fake_decisions = [
        [('position', 'buy'), ('volume', 1), ('ticker', 'pltr')],
        [('position', 'sell'), ('volume', 1), ('ticker', 'pltr')],
        [('position', 'noop')],
    ]
    random_signal = random.choice(fake_decisions)
    signal_json = json.dumps(dict(random_signal))
    return signal_json