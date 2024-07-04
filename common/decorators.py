import asyncio
import websockets
from functools import wraps
import sys

def backoff_reconnect(max_backoff=60):
    def decorator(some_layer_entrypoint):
        @wraps(some_layer_entrypoint)
        async def wrapper(socket_url, *args, **kwargs):
            backoff = 1
            while True:
                try:
                    print(f"Trying to connect to {socket_url}")
                    sys.stdout.flush()
                    connection = await websockets.connect(socket_url)
                    print(f"Connected to {socket_url}")
                    sys.stdout.flush()
                    backoff = 1
                    return await some_layer_entrypoint(connection, *args, **kwargs)
                except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK, OSError) as e:
                    print(f"Connection failed: {e}")
                    sys.stdout.flush()
                    print(f"Reconnecting in {backoff} seconds...")
                    sys.stdout.flush()
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
        return wrapper
    return decorator
