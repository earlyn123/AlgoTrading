import asyncio
import websockets
from functools import wraps

def backoff_reconnect(max_backoff=60):
    def decorator(some_layer_entrypoint):
        @wraps(some_layer_entrypoint)
        async def wrapper(socket_url, *args, **kwargs):
            backoff = 1
            while True:
                try:
                    print(f"Trying to connect to {socket_url}")
                    async with websockets.connect(socket_url) as ws:
                        print(f"Connected to {socket_url}")
                        backoff = 1
                        return await some_layer_entrypoint(ws, *args, **kwargs)
                except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK, OSError) as e:
                    print(f"Connection failed: {e}")
                    print(f"Reconnecting in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
        return wrapper
    return decorator