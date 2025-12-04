from django.db import models
from django.conf import settings  # safe

class Vendor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ safe reference
        on_delete=models.CASCADE,
        related_name='shop_vendor_profile'
    )
    shop_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
