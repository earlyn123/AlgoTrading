import websockets

async def send_socket_message(message, ws):
    try:
        await ws.send(message)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
        raise
    except Exception as e:
        print(f"Error sending message: {e}")
        raise