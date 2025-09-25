import asyncio
import websockets

clientes = set()

async def handler(websocket):
    clientes.add(websocket)
    try:
        async for message in websocket:
            await asyncio.wait([c.send(message) for c in clientes if c != websocket])
    finally:
        clientes.remove(websocket)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Servidor WebSocket rodando em ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
