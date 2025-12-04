from django.shortcuts import render, redirect
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
import json
from django.template.loader import render_to_string
from core.models import CartOrder,CartOrderProducts, Product, Category, ProductReview
from userauths.models import Profile, User,ContactUs
from vendor.forms import AddProductForm
from vendor.decorators import vendor_required

import datetime

from django.db.models import Sum, Q
import datetime
from django.shortcuts import render
from core.models import CartOrderProducts, Product, CartOrder
from django.db.models import Sum
import datetime
# Add these imports at the top of your views.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import os

# ---------------------------
# Load shipment data and train models (global, once)
# ---------------------------
shipment_csv = os.path.join("vendor", "shipment_data.csv")  # adjust path
df_ship = pd.read_csv(shipment_csv)

# Encode categorical columns
le_origin = LabelEncoder()
le_destination = LabelEncoder()
le_method = LabelEncoder()
df_ship["Origin_enc"] = le_origin.fit_transform(df_ship["Origin"])
df_ship["Destination_enc"] = le_destination.fit_transform(df_ship["Destination"])
df_ship["Method_enc"] = le_method.fit_transform(df_ship["Method"])

# Train RandomForest models
X_ship = df_ship[["Origin_enc", "Destination_enc", "Weight", "Method_enc"]]
y_time = df_ship["DeliveryTimeDays"]
y_cost = df_ship["CostETB"]

time_model = RandomForestRegressor(n_estimators=100, random_state=42)
time_model.fit(X_ship, y_time)

cost_model = RandomForestRegressor(n_estimators=100, random_state=42)
cost_model.fit(X_ship, y_cost)



@vendor_required
def dashboard(request):
    user = request.user  # logged-in vendor
    
    # All products belonging to this vendor
    all_products = Product.objects.filter(user=user)
    product_titles = [p.title for p in all_products]
    
    # All order items belonging to this vendor's products
    from django.db.models import Q
    vendor_order_items = CartOrderProducts.objects.none()
    for title in product_titles:
        vendor_order_items |= CartOrderProducts.objects.filter(item__iexact=title)
    
    # Revenue: sum of total of all order items
    revenue = vendor_order_items.aggregate(total_revenue=Sum("total"))["total_revenue"] or 0
    
    # Total orders (unique orders)
    total_orders_count = vendor_order_items.values('order').distinct().count()
    
    # Latest orders (unique orders)
    latest_order_ids = vendor_order_items.values_list('order', flat=True).distinct()
    latest_orders = CartOrder.objects.filter(id__in=latest_order_ids).order_by('-order_date')[:10]
    
    # Monthly revenue (orders placed this month)
    this_month = datetime.datetime.now().month
    monthly_revenue = vendor_order_items.filter(order__order_date__month=this_month).aggregate(total_revenue=Sum("total"))["total_revenue"] or 0
    
    context = {
        "revenue": revenue,
        "total_orders_count": total_orders_count,
        "all_products": all_products,
        "monthly_revenue": monthly_revenue,
        "latest_orders": latest_orders,
    }
    
    return render(request, "vendor/dashboard.html", context)


@vendor_required
def products(request): 
    all_categories = Category.objects.all()

    # Get the status filter from query params
    status_filter = request.GET.get("status", "").lower()  # '' / 'draft' / 'published' / 'disabled'

    # All products for the logged-in vendor
    all_products = Product.objects.filter(user=request.user)

    # Count products by status
    status_counts = {
        "published": all_products.filter(product_status="published").count(),
        "draft": all_products.filter(product_status="draft").count(),
        "disabled": all_products.filter(product_status="disabled").count(),
        "all": all_products.count(),
    }

    # Apply filter if selected
    if status_filter in ["draft", "disabled", "published"]:
        all_products = all_products.filter(product_status=status_filter)

    context = {
        "all_products": all_products,
        "all_categories": all_categories,
        "status_filter": status_filter,
        "status_counts": status_counts,
    }
    return render(request, "vendor/products.html", context)






@vendor_required
def latest_orders_partial(request):
    user = request.user
    all_products = Product.objects.filter(user=user)
    product_titles = [p.title for p in all_products]

    vendor_order_items = CartOrderProducts.objects.none()
    for title in product_titles:
        vendor_order_items |= CartOrderProducts.objects.filter(item__iexact=title)

    latest_order_ids = vendor_order_items.values_list('order', flat=True).distinct()
    latest_orders = CartOrder.objects.filter(id__in=latest_order_ids).order_by('-order_date')[:10]

    html = render_to_string("vendor/latest_orders_rows.html", {
        "latest_orders": latest_orders
    })

    return JsonResponse({"html": html})
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import json



@csrf_exempt
@vendor_required
def confirm_product(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("item_id")
        status = data.get("status")

        try:
            # Ensure the product belongs to the vendor
            item = CartOrderProducts.objects.get(id=item_id, product__user=request.user)
            item.vendor_confirmation = status
            item.save()

            product = item.product
            vendor_user = product.user
            order = item.order
            order_user = order.user

            # ---------------------------
            # Predict best delivery method dynamically
            # ---------------------------
            product_weight = item.qty  # adjust if you have a separate weight field
            origin = order.city        # adjust if you store differently
            destination = order.address  # adjust if you store differently

            best_option = None
            # Evaluate all methods in CSV
            methods = df_ship["Method"].unique()
            predictions = []

            for method in methods:
                # Create input for prediction
                inp = pd.DataFrame([{
                    "Origin_enc": le_origin.transform([origin])[0] if origin in le_origin.classes_ else 0,
                    "Destination_enc": le_destination.transform([destination])[0] if destination in le_destination.classes_ else 0,
                    "Weight": product_weight,
                    "Method_enc": le_method.transform([method])[0]
                }])
                pred_time = time_model.predict(inp)[0]
                pred_cost = cost_model.predict(inp)[0]
                predictions.append({
                    "Method": method,
                    "pred_time": pred_time,
                    "pred_cost": pred_cost
                })

            # Select best: prioritize fastest, then cheapest
            best_option = sorted(predictions, key=lambda x: (x["pred_time"], x["pred_cost"]))[0]

            # ---------------------------
            # Send email
            # ---------------------------
            message = f"""
Hello Delivery Team,

The vendor has confirmed the product for delivery.

--- Vendor Info ---
Vendor Name: {vendor_user.username}
Vendor Email: {vendor_user.email}
Vendor Bio: {vendor_user.bio if hasattr(vendor_user, 'bio') else '-'}
Vendor Phone: {vendor_user.phone if hasattr(vendor_user, 'phone') else '-'}

--- Customer / Buyer Info ---
Customer Name: {order.full_name or order_user.username}
Customer Email: {order.email or order_user.email}
Customer Phone: {order.phone or '-'}
Shipping Address: {order.address}, {order.city}, {order.state}, {order.country}

--- Product Info ---
Product Title: {product.title}
Quantity: {item.qty}
Unit Price: ${item.price}
Total: ${item.total}
Invoice No: {item.invoice_no}

--- Recommended Delivery Method ---
Method: {best_option['Method']}
Estimated Delivery Time: {round(best_option['pred_time'], 1)} days
Estimated Cost: {round(best_option['pred_cost'], 2)} ETB
"""

            send_mail(
                subject=f"Delivery Request: Order {order.oid}",
                message=message,
                from_email="christge2121@gmail.com",
                recipient_list=["christanchristan128@gmail.com"],
                fail_silently=True,
            )

            return JsonResponse({"success": True})

        except CartOrderProducts.DoesNotExist:
            return JsonResponse({"success": False, "error": "Item not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})

    
@vendor_required
def change_product_status(request, pid):
    product = Product.objects.get(pid=pid, user=request.user)  # Only allow logged-in user to change their product
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["published", "draft", "disabled"]:
            product.product_status = new_status
            product.save()
    return redirect("vendor:dashboard-products")
@vendor_required
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            action = request.POST.get("action")
            if action == "draft":
                product.product_status = "draft"
            elif action == "publish":
                product.product_status = "published"
            product.user = request.user
            product.save()
            form.save_m2m()
            return redirect("dashboard-products")
    else:
        form = AddProductForm()

    return render(request, "vendor/add-products.html", {"form": form})

@vendor_required
def edit_product(request, pid):
    product = Product.objects.get(pid=pid)

    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.save()
            form.save_m2m()
            return redirect("vendor:dashboard-products")
    else:
        form = AddProductForm(instance=product)
    context = {
        'form':form,
        'product':product,
    }
    return render(request, "vendor/edit-products.html", context)

@vendor_required
def delete_product(request, pid):
    product = Product.objects.get(pid=pid)
    product.delete()
    return redirect("vendor:dashboard-products")

@vendor_required
def orders(request):
    orders = CartOrder.objects.all()
    context = {
        'orders':orders,
    }
    return render(request, "vendor/orders.html", context)


@vendor_required
def orderss(request):
    orders = ContactUs.objects.all()
    context = {
        'orderss':orders,
    }
    return render(request, "vendor/orderss.html", context)


@vendor_required
def vendor_dashboard(request):
    orders = ContactUs.objects.all()
    context = {
        'orderss':orders,
    }
    return render(request, "vendor/vendor_dashboard.html", context)


@vendor_required
def ordersss(request):
    
    orders = User.objects.all()
    context = {
        'orderss':orders,
    }
    return render(request, "vendor/cont.html", context)
@vendor_required
def order_detail(request, id):
    order = CartOrder.objects.get(id=id)
    order_items = CartOrderProducts.objects.filter(order=order)
    context = {
        'order':order,
        'order_items':order_items
    }
    return render(request, "vendor/order_detail.html", context)

@vendor_required
@csrf_exempt
def change_order_status(request, oid):
    order = CartOrder.objects.get(oid=oid)
    if request.method == "POST":
        status = request.POST.get("status")
        print("status =======", status)
        messages.success(request, f"Order status changed to {status}")
        order.product_status = status
        order.save()
    
    return redirect("vendor:order_detail", order.id)

@vendor_required
def shop_page(request):
    products = Product.objects.filter(user=request.user)
    revenue = CartOrder.objects.filter(paid_status=True).aggregate(price=Sum("price"))
    total_sales = CartOrderProducts.objects.filter(order__paid_status=True).aggregate(qty=Sum("qty"))

    context = {
        'products':products,
        'revenue':revenue,
        'total_sales':total_sales,
    }
    return render(request, "vendor/shop_page.html", context)

@vendor_required
def reviews(request):
    reviews = ProductReview.objects.all()
    context = {
        'reviews':reviews,
    }
    return render(request, "vendor/reviews.html", context)

@vendor_required
def settings(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        image = request.FILES.get("image")
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        bio = request.POST.get("bio")
        address = request.POST.get("address")
        country = request.POST.get("country")
        print("image ===========", image)
        
        if image != None:
            profile.image = image
        profile.full_name = full_name
        profile.phone = phone
        profile.bio = bio
        profile.address = address
        profile.country = country

        profile.save()
        messages.success(request, "Profile Updated Successfully")
        return redirect("vendor:settings")
    
    context = {
        'profile':profile,
    }
    return render(request, "vendor/settings.html", context)

@vendor_required
def change_password(request):
    user = request.user

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        if confirm_new_password != new_password:
            messages.error(request, "Confirm Password and New Password Does Not Match")
            return redirect("vendor:change_password")
        
        if check_password(old_password, user.password):
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password Changed Successfully")
            return redirect("vendor:change_password")
        else:
            messages.error(request, "Old password is not correct")
            return redirect("vendor:change_password")
    
    return render(request, "vendor/change_password.html")
