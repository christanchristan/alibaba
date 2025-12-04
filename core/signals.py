# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import CartOrder, CartOrderProducts

@receiver(post_save, sender=CartOrder)
def send_vendor_notification(sender, instance, created, **kwargs):
    """
    Automatically notify vendors when an order is paid.
    """
    if not created and instance.paid_status:  # only trigger when an existing order is marked paid
        channel_layer = get_channel_layer()
        cart_items_qs = CartOrderProducts.objects.filter(order=instance)

        for item in cart_items_qs:
            if hasattr(item, 'vendor') and item.vendor:
                vendor_group_name = f'vendor_{item.vendor.id}'

                async_to_sync(channel_layer.group_send)(
                    vendor_group_name,
                    {
                        "type": "vendor_notification",
                        "message": f"Your product '{item.item}' has been paid!",
                        "order_id": instance.oid,
                        "product_id": item.id,
                        "amount": float(item.total),
                    }
                )
