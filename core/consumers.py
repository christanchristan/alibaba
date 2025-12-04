from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class VendorNotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        # Reject anonymous users
        if user.is_anonymous:
            await self.send(text_data=json.dumps({
                "error": "Authentication required. Please log in."
            }))
            await self.close(code=4001)
            return

        self.vendor_user = user
        self.group_name = f"vendor_{self.vendor_user.id}"

        # Add this socket to the vendor group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def vendor_notification(self, event):
        """
        Regular vendor notification (informational).
        """
        await self.send(text_data=json.dumps({
            "type": "vendor_notification",
            "message": event.get("message"),
            "order_id": event.get("order_id"),
            "product_id": event.get("product_id"),
            "amount": event.get("amount"),
        }))

    async def order_paid(self, event):
        """
        Triggered only when a new payment is completed and the item was previously unpaid.
        """
        await self.send(text_data=json.dumps({
            "type": "order_paid",
            "item_id": event.get("item_id"),
            "order_id": event.get("order_id"),
            "product_id": event.get("product_id"),
            "amount": event.get("amount"),
            "message": event.get("message"),
        }))
