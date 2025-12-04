# filename: test_car_tracking.py
import asyncio
import websockets
import json

async def test_car_tracking():
    uri = "ws://localhost:8000/ws/car_tracking/"
    async with websockets.connect(uri) as websocket:
        print("✅ Connected")
        await websocket.send(json.dumps({"car_id": 1, "latitude": 12.9716, "longitude": 77.5946}))
        response = await websocket.recv()
        print("📍 Received:", response)

asyncio.run(test_car_tracking())
