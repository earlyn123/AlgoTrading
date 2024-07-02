import asyncio
import signal

async def shutdown(server, loop, tasks):
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    server.close()
    await server.wait_closed()
    loop.stop()

def setup_signal_handlers(server, loop, tasks):
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(
            getattr(signal, signame),
            lambda: asyncio.create_task(shutdown(server, loop, tasks))
        )
