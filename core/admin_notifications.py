from django.contrib import admin
from django.urls import path
from django.shortcuts import render


def admin_notifications(request):
    notifications = [
        {"message": "New user registered", "level": "info"},
        {"message": "Order #1234 pending", "level": "warning"},
    ]
    return render(request, "admin/notifications.html", {"notifications": notifications})


def get_admin_urls():
    # Get original URLs ONCE
    orig_urls = admin.site.get_urls_without_custom

    def wrap(view):
        return admin.site.admin_view(view)

    custom_urls = [
        path("notifications/", wrap(admin_notifications), name="admin-notifications"),
    ]

    return custom_urls + orig_urls()


# Monkey-patch safely
if not hasattr(admin.site, "get_urls_without_custom"):
    admin.site.get_urls_without_custom = admin.site.get_urls
    admin.site.get_urls = get_admin_urls
