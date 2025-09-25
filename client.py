import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("Conectado ao servidor")
        while True:
            msg = await websocket.recv()
            print(f"Tradução recebida: {msg}")

if __name__ == "__main__":
    asyncio.run(listen())
