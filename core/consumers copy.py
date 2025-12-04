import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CarTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "car_tracking_group"  # ✅ Group name
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"✅ Client connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"❌ Client disconnected: {self.channel_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        car_id = data.get("car_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if car_id is None or latitude is None or longitude is None:
            print("⚠️ Invalid data received:", data)
            return

        print(f"🚗 Car {car_id} location update: {latitude}, {longitude}")

        # Broadcast the update to all clients in the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "car_location_update",  # maps to `car_location_update` method
                "car_id": car_id,
                "latitude": latitude,
                "longitude": longitude
            }
        )

    async def car_location_update(self, event):
        # Send the location update to the WebSocket client
        await self.send(text_data=json.dumps({
            "car_id": event["car_id"],
            "lat": event["latitude"],
            "lng": event["longitude"]
        }))
