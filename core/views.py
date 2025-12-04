
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from requests import session
from django.conf import settings
import stripe
from taggit.models import Tag
from django.db.models import Min, Max
from userauths.models import User  # your custom user model

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from core.models import Coupon, Product, Category, Vendor, CartOrder, CartOrderProducts, ProductImages, ProductReview, wishlist_model, Address
from userauths.models import ContactUs, Profile,User
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import Settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json  # <-- Make sure this is included
from core.models import CartOrder, CartOrderProducts

import calendar
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth
from django.core import serializers
car_locations = {}






car_locations = {}

@csrf_exempt
def car_join(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            uuid_car = data.get("uuid")
            lat = data.get("lat")
            long = data.get("long")
            degree = data.get("degree")

            if not all([uuid_car, lat, long, degree]):
                return JsonResponse({"status": 0, "message": "Missing parameters"})

            car_locations[uuid_car] = {"uuid": uuid_car, "lat": lat, "long": long, "degree": degree}

            # Send to WebSocket group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "car_tracking_group",  # Must match your consumer
                {
                    "type": "car_location_update",
                    "car_id": uuid_car,
                    "latitude": lat,
                    "longitude": long
                }
            )

            return JsonResponse({"status": 1, "payload": car_locations, "message": "successfully"})
        except Exception as e:
            return JsonResponse({"status": 0, "message": str(e)})

    return JsonResponse({"status": 0, "message": "Invalid request method"})

@csrf_exempt
def car_update_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            car_id = data.get("uuid")  # match your Flutter car UUID
            lat = data.get("lat")
            lng = data.get("long")

            if not all([car_id, lat, lng]):
                return JsonResponse({"status": 0, "message": "Missing parameters"})

            # Save/update car location
            car_locations[car_id] = {"car_id": car_id, "latitude": lat, "longitude": lng}

            # Send to WebSocket group (must match consumer)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "car_tracking_group",  # ✅ Same as consumer
                {
                    "type": "car_location_update",
                    "car_id": car_id,
                    "latitude": lat,
                    "longitude": lng
                }
            )

            return JsonResponse({"status": 1, "message": "Location updated successfully"})
        except Exception as e:
            return JsonResponse({"status": 0, "message": str(e)})

    return JsonResponse({"status": 0, "message": "Invalid request method"})

def index(request):
    # bannanas = Product.objects.all().order_by("-id")
    products = Product.objects.filter(product_status="published", featured=True).order_by("-id")

    context = {
        "products":products
    }

    return render(request, 'core/index.html', context)














import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Temporary storage for demo; in production, use a database model
verification_codes = {}

# ------------------------------
# 1. Send verification code
# ------------------------------
@csrf_exempt
def send_email_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({"success": False, "error": "Email is required."})

            # Generate 6-digit code
            code = str(random.randint(100000, 999999))
            expires_at = datetime.now() + timedelta(minutes=10)  # Code valid for 10 min
            verification_codes[email] = {"code": code, "expires": expires_at}

            # Send email (configure EMAIL_BACKEND in settings.py)
            send_mail(
                subject="Your Verification Code",
                message=f"Your verification code is {code}",
                from_email="no-reply@yourdomain.com",
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


# ------------------------------
# 2. Verify the code
# ------------------------------
@csrf_exempt
def verify_email_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')

            if not email or not code:
                return JsonResponse({"success": False, "error": "Email and code are required."})

            record = verification_codes.get(email)
            if not record:
                return JsonResponse({"success": False, "error": "No verification code found."})

            if record["expires"] < datetime.now():
                del verification_codes[email]
                return JsonResponse({"success": False, "error": "Verification code expired."})

            if record["code"] != code:
                return JsonResponse({"success": False, "error": "Invalid verification code."})

            # Success: remove the code from memory
            del verification_codes[email]

            # Optionally: mark email as verified in session or database
            request.session['verified_email'] = email

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})

GOOGLE_CLIENT_ID = "220674381580-vee67c9fb0c8lki4u6pv5tuin8lcqie7.apps.googleusercontent.com"




import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from core.models import User  # adjust import if your User model is elsewhere

import json
import requests
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
GOOGLE_CLIENT_ID = "220674381580-vee67c9fb0c8lki4u6pv5tuin8lcqie7.apps.googleusercontent.com"


@csrf_exempt
def google_one_tap_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        body = json.loads(request.body)
        credential = body.get("credential")

        if not credential:
            return JsonResponse({"error": "Missing credential"}, status=400)

        # Verify token using Google's official library
        idinfo = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("name", "User")

        if not email:
            return JsonResponse({"error": "Email not provided by Google"}, status=400)

        # Get or create the user
        user, _ = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": name
            }
        )

        login(request, user)
        return JsonResponse({"success": True, "message": "Logged in successfully"})

    except ValueError:
        return JsonResponse({"error": "Invalid token"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.db.models import F, FloatField, ExpressionWrapper, Min, Max

def product_list_view(request):
    # Get published products
    products = Product.objects.filter(product_status="published").order_by("-id")

    # Annotate products with price + 10%
    products = products.annotate(
        price_plus_10=ExpressionWrapper(
            F('price') * 1.10,  # original price + 10%
            output_field=FloatField()
        )
    )

    # Get tags
    tags = Tag.objects.all().order_by("-id")[:6]

    # Add categories and vendors
    categories = Category.objects.all()
    vendors = Vendor.objects.all()

    # Get min/max price for the slider (including 10% increase)
    min_max_price = products.aggregate(
        price__min=Min(F('price') * 1.10),
        price__max=Max(F('price') * 1.10)
    )

    context = {
        "products": products,
        "tags": tags,
        "categories": categories,
        "vendors": vendors,
        "min_max_price": min_max_price,
    }

    return render(request, 'core/product-list.html', context)

 


def category_list_view(request):
    categories = Category.objects.all()

    context = {
        "categories":categories
    }
    return render(request, 'core/category-list.html', context)



def category_product_list__view(request, cid):

    category = Category.objects.get(cid=cid) # food, Cosmetics
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category":category,
        "products":products,
    }
    return render(request, "core/category-product-list.html", context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    # product = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    # Getting all reviews related to a product
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

    # Getting average review
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Product Review form
    review_form = ProductReviewForm()


    make_review = True 

    if request.user.is_authenticated:
       
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False
    
    address = "Login To Continue"


    p_image = product.p_images.all()

    context = {
        "p": product,
        "address": address,
        "make_review": make_review,
        "review_form": review_form,
        "p_image": p_image,
        "average_rating": average_rating,
        "reviews": reviews,
        "products": products,
    }

    return render(request, "core/product-detail.html", context)

def tag_list(request, tag_slug=None):

    products = Product.objects.filter(product_status="published").order_by("-id")

    tag = None 
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products": products,
        "tag": tag
    }

    return render(request, "core/tag.html", context)


def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user 

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
       {
         'bool': True,
        'context': context,
        'average_reviews': average_reviews
       }
    )


def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)


def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")


    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)


    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct() 
    else:
        products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct() 
    else:
        products = Product.objects.filter(product_status="published").order_by("-id").distinct()    
    
       

    
    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})


def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:

            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data

    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})

 

 




def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")
def cart_views(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/carts.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})






from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def delete_cart_item(request, product_id):
    product_id = str(product_id)  # session key is string
    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        if product_id in cart_data:
            del cart_data[product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = sum(int(item['qty']) * float(item['price']) for item in request.session.get('cart_data_obj', {}).values())

    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session.get('cart_data_obj', {}),
        'totalcartitems': len(request.session.get('cart_data_obj', {})),
        'cart_total_amount': cart_total_amount
    })
    return JsonResponse({"data": context, "totalcartitems": len(request.session.get('cart_data_obj', {}))})


@csrf_exempt
def update_cart_item(request, product_id):
    product_id = str(product_id)
    qty = request.POST.get('qty') or request.GET.get('qty')  # get qty from POST/GET

    if 'cart_data_obj' in request.session and product_id in request.session['cart_data_obj']:
        cart_data = request.session['cart_data_obj']
        cart_data[product_id]['qty'] = int(qty)
        request.session['cart_data_obj'] = cart_data

    cart_total_amount = sum(int(item['qty']) * float(item['price']) for item in request.session.get('cart_data_obj', {}).values())

    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session.get('cart_data_obj', {}),
        'totalcartitems': len(request.session.get('cart_data_obj', {})),
        'cart_total_amount': cart_total_amount
    })
    return JsonResponse({"data": context, "totalcartitems": len(request.session.get('cart_data_obj', {}))})



def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from core.models import CartOrder

def verify_chapa_payment(request, order_id):
    # 1) Find the order
    order = get_object_or_404(CartOrder, oid=order_id)

    # 2) Build Chapa verify URL
    verify_url = f"https://api.chapa.co/v1/transaction/verify/{order_id}"

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # 3) Call Chapa verification endpoint
    response = requests.get(verify_url, headers=headers)
    data = response.json()

    # DEBUG — print the raw response
    print("🔍 Chapa Verification Response:", data)

    # 4) Check payment status
    if data.get("status") == "success" and data["data"]["status"] == "success":
        order.paid_status = True
        order.product_status = "Paid"
        order.save()

        return JsonResponse({"status": "success", "message": "Payment verified!"})

    return JsonResponse({"status": "failed", "message": "Payment not verified."})

@login_required
def checkout_view(request, oid):
    # Fetch order and its items
    order = get_object_or_404(CartOrder, oid=oid, user=request.user)
    order_items = CartOrderProducts.objects.filter(order=order)
    # Test accounts (if you want to display test info)
    test_user_amole = {"phone": "0912345678", "otp": "1234"}  # replace with your test data
    test_user_awash = {"phone": "0945678901", "otp": "5678"}
    test_card = {"provider": "Visa", "number": "4242 4242 4242 4242", "cvv": "123", "expiry": "12/34"}

    # PayPal button
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': order.price,
        'item_name': f"Order-Item-No-{order.oid}",
        'invoice': f"INVOICE_NO-{order.oid}",
        'currency_code': "USD",
        'notify_url': f"http://{host}{reverse('core:paypal-ipn')}",
        'cancel_url': f"http://{host}{reverse('core:payment-failed')}",
    }
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    context = {
        "order": order,
        "order_items": order_items,
        "stripe_publishable_key": settings.STRIPE_PUBLIC_KEY,
        "paypal_payment_button": paypal_payment_button,
        "test_user_amole": test_user_amole,
        "test_user_awash": test_user_awash,
        "test_card": test_card,
    }

    return render(request, "core/checkout.html", context)

@csrf_exempt
@login_required
def test_chapa_payment(request):
    if request.method != "POST":
        return JsonResponse({"status": "failed", "message": "Invalid request method"})

    try:
        print("Raw request body:", request.body)
        data = json.loads(request.body)

        # Read required fields
        amount = data.get("amount")
        currency = data.get("currency", "ETB")
        email = data.get("email")
        first_name = data.get("first_name", "Test")
        last_name = data.get("last_name")
        phone_number = data.get("phone")

        # Get existing order from session
        order_oid = request.session.get('order_oid')
        if not order_oid:
            return JsonResponse({"status": "failed", "message": "Order OID is missing. Please start checkout again."})

        # Fetch the existing order
        order = get_object_or_404(CartOrder, oid=order_oid, user=request.user)
        print(f"Using existing order: {order.oid}, paid_status: {order.paid_status}")

        if not amount:
            return JsonResponse({"status": "failed", "message": "Amount is required."})

        # Generate unique transaction reference
        tx_ref = f"test-{uuid.uuid4().hex[:10]}"

        # Chapa return URL points to payment_completed_view
        return_url = f"http://127.0.0.1:8000/payment-completed/{order.oid}/"

        # Chapa payment payload
        payload = {
            "amount": amount,
            "currency": currency,
            "tx_ref": tx_ref,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "callback_url": "http://localhost:8000/chapa-callback/",
            "return_url": return_url,
            "customization": {
                "title": "Bank Payment",
                "description": "Sandbox payment integration"
            }
        }

        headers = {
            "Authorization": "Bearer CHASECK_TEST-1N3WI3fzu7Nr9JURNJ3l3GBf30U5xqSL",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.chapa.co/v1/transaction/initialize",
            headers=headers,
            json=payload,
        )

        result = response.json()
        print("Chapa Response:", result)

        if result.get("status") == "success":
            return JsonResponse({
                "status": "success",
                "payment_url": result["data"]["checkout_url"],
                "tx_ref": tx_ref,
                "order_oid": order.oid,
            })

        return JsonResponse({
            "status": "failed",
            "message": result.get("message", "Unknown error")
        })

    except Exception as e:
        print("Error initializing Chapa transaction:", e)
        return JsonResponse({"status": "failed", "message": str(e)})



def calculate_shipping(origin, destination, weight):
    """
    Call TrackingMore API to get shipping cost and estimated delivery days.
    """
    url = "https://api.trackingmore.com/v2/trackings/ethiopianpost/calculate"
    payload = {
        "origin": origin,
        "destination": destination,
        "weight": weight,
    }
    headers = {
        "Tracking-Api-Key": "98d2octl-brgb-ssej-lb5t-ii1g12kjo6om",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        shipping_cost = data.get("shipping_cost", 0)
        estimated_days = data.get("estimated_days", None)
        print("📦 Shipping cost:", shipping_cost)
        print("⏳ Estimated delivery days:", estimated_days)
        return shipping_cost, estimated_days
    except requests.RequestException as e:
        print("🔥 Shipping API error:", e)
        return 0, None

@login_required
def save_checkout_info(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("core:cart")

    # 1️⃣ Get form data
    full_name = request.POST.get("full_name")
    email = request.POST.get("email")
    mobile = request.POST.get("mobile")
    address = request.POST.get("address")
    city = request.POST.get("city")
    state = request.POST.get("state")
    country = request.POST.get("country")

    # 2️⃣ Save temporarily in session (optional)
    request.session.update({
        'full_name': full_name,
        'email': email,
        'mobile': mobile,
        'address': address,
        'city': city,
        'state': state,
        'country': country,
    })

    # 3️⃣ Ensure cart exists
    cart = request.session.get("cart_data_obj")
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect("core:index")

    # 4️⃣ Calculate total amount and total weight
    total_amount = 0
    total_weight = 0
    for item in cart.values():
        qty = int(item['qty'])
        price = float(item['price'])
        total_amount += qty * price

        product_obj = Product.objects.filter(pid=item.get("pid")).first()
        if product_obj and hasattr(product_obj, 'weight'):
            total_weight += product_obj.weight * qty

    # 5️⃣ Calculate shipping
    origin_address = "Addis Ababa, Ethiopia"  # Warehouse
    destination_address = f"{address}, {city}, {state}, {country}"
    shipping_cost, estimated_days = calculate_shipping(origin_address, destination_address, total_weight)

    if not shipping_cost:
        shipping_cost = 300
    if not estimated_days:
        estimated_days = 3  # or None if you prefer
    print("💰 Total cart amount:", total_amount)
    print("📦 Shipping cost to pass to template:", shipping_cost)

    # 6️⃣ Get client IP and location
    customer_ip = get_client_ip(request)
    print("🖥 Customer IP:", customer_ip)

    location = None
    if customer_ip not in ("127.0.0.1", "::1"):  # Skip IPStack for localhost
        location = get_location_from_ip(customer_ip)
    print("📍 Location from IPStack:", location)

    # 7️⃣ Determine customer_center city with fallback
    cityapi = location['city'] if location and location.get('city') else city or "Addis Ababa"
    print("📦 customer_center:", cityapi)

    # 8️⃣ Total including shipping
    total_amount_with_shipping = total_amount + shipping_cost

    # 9️⃣ Create CartOrder
    order = CartOrder.objects.create(
        user=request.user,
        total_price=total_amount,
        price=total_amount_with_shipping,
        shipping_cost=shipping_cost,
        shipping_estimate=estimated_days,
        full_name=full_name,
        email=email,
        phone=mobile,
        address=address,
        city=city,
        state=state,
        country=country,
    )

    request.session['order_oid'] = order.oid

    # 🔟 Create CartOrderProducts for each item
    for item in cart.values():
        product_obj = Product.objects.filter(pid=item.get("pid")).first()
        vendor_obj = product_obj.vendor if product_obj else None

        vendor_state = product_obj.user.state if product_obj and product_obj.user else None
        CartOrderProducts.objects.create(
            order=order,
            vendor=vendor_obj,
            invoice_no=f"INVOICE_NO-{order.id}",
            product_status="Pending",
            item=item['title'],
            image=item['image'],
            qty=int(item['qty']),
            price=float(item['price']),
            total=int(item['qty']) * float(item['price']),
            product=product_obj,
            vendor_center=vendor_state,
            customer_center=cityapi
        )

    # 1️⃣1️⃣ Clear temporary session checkout info
    for key in ['full_name', 'email', 'mobile', 'address', 'city', 'state', 'country']:
        request.session.pop(key, None)

    # 1️⃣2️⃣ Redirect to checkout page with order and shipping info
    return redirect("core:checkout", order.oid)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

IPSTACK_API_KEY = "ef2cea655244fddbd0f4692df1a7e6d7"

def get_location_from_ip(ip_address):
    """
    Use IPStack API to get location details from an IP address.
    Returns a dict with city, region, country, etc.
    """
    url = f"http://api.ipstack.com/{ip_address}?access_key={IPSTACK_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "city": data.get("city"),
            "region": data.get("region_name"),
            "country": data.get("country_name"),
        }
    except Exception as e:
        print("Error fetching location:", e)
        return None
    
    

@csrf_exempt

def create_checkout_session(request, oid):
    order = CartOrder.objects.get(oid=oid)
  

    checkout_session = stripe.checkout.Session.create(
        customer_email = order.email,
        payment_method_types=['card'],
        line_items = [
            {
                'price_data': {
                    'currency': 'USD',
                    'product_data': {
                        'name': order.full_name
                    },
                    'unit_amount': int(order.price * 100)
                },
                'quantity': 1
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid]))
    )

    order.paid_status = False
    order.stripe_payment_intent = checkout_session['id']
    order.save()

    print("checkkout session", checkout_session)
    return JsonResponse({"sessionId": checkout_session.id})




@login_required
def checkout(request, oid):
    order = CartOrder.objects.get(oid=oid)
    order_items = CartOrderProducts.objects.filter(order=order)

   
    if request.method == "POST":
        code = request.POST.get("code")
        print("code ========", code)
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            if coupon in order.coupons.all():
                messages.warning(request, "Coupon already activated")
                return redirect("core:checkout", order.oid)
            else:
                discount = order.price * coupon.discount / 100 

                order.coupons.add(coupon)
                order.price -= discount
                order.saved += discount
                order.save()

                messages.success(request, "Coupon Activated")
                return redirect("core:checkout", order.oid)
        else:
            messages.error(request, "Coupon Does Not Exists")

        

    context = {
        "order": order,
        "order_items": order_items,
        

    }
    return render(request, "core/checkout.html", context)





@csrf_exempt  # Allow POST without CSRF token (for testing)
def test_mobile_money(request):
    print("✅ test_mobile_money view called")  # Debug log in console


    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = data.get("phone")
            otp = data.get("otp")
            order_id = data.get("order_id")

            print(f"📩 Received data: phone={phone}, otp={otp}, order_id={order_id}")

            # Test payment verification
            if phone == "0900123456" and otp == "12345":
                print("✅ OTP matched, returning success.")
                return JsonResponse({
                    "status": "success",
                    "transaction_id": "TX123456",
                    "order_id": order_id
                })
            else:
                print("❌ Invalid OTP or phone.")
                return JsonResponse({
                    "status": "failed",
                    "message": "Invalid OTP or phone number"
                })
        except Exception as e:
            print(f"🔥 Error parsing request: {e}")
            return JsonResponse({"status": "failed", "message": str(e)})

    print("⚠️ Invalid request method.")
    return JsonResponse({"status": "failed", "message": "Invalid request"})





CHAPA_SECRET_KEY = "CHAPUBK_TEST-ptWPjWpjl81OI19Hr82yg360dw8qnmfn"

def pay_with_chapa(phone, amount):
    url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
    data = {
        "amount": amount,
        "currency": "ETB",
        "tx_ref": "TX12345", 
        "phone_number": phone,
        "callback_url": "http://localhost:8000/callback/"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
import sys

def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published").order_by("-id")

    context = {
        "vendor": vendor,
        "products": products,
    }
    return render(request, "core/vendor-detail.html", context)



@login_required
def payment_completed_view(request, oid=None):
    def log(*args):
        print(*args, file=sys.stdout)
        sys.stdout.flush()

    # Get order ID from URL or session
    order_oid = oid or request.session.get('order_oid')
    if not order_oid:
        log("⚠️ Order OID not found in URL or session")
        return redirect('core:cart')

    # Retrieve order
    order = get_object_or_404(CartOrder, oid=order_oid, user=request.user)
    log(f"✅ Payment completed for order {order.oid}, user: {request.user.username}")

    # If payment just completed
    if not order.paid_status:
        order.paid_status = True
        order.product_status = "Paid"
        order.save()
        log("💰 Order marked as paid")

        # Clear session data
        request.session.pop('cart_data_obj', None)
        request.session.pop('order_oid', None)
        log("🗑️ Cleared cart session data")

        # Real-time vendor notifications
        channel_layer = get_channel_layer()
        cart_items_qs = CartOrderProducts.objects.filter(order=order)
        log(f"🛒 Found {cart_items_qs.count()} items in order")

        sent_notifications = set()  # Keep track of sent notifications

        for item in cart_items_qs:
            product = item.product
            if not product:
                log(f"❌ Product missing for CartOrderProducts id {item.id}")
                continue

            vendor_user = product.user
            if not vendor_user:
                log(f"⚠️ Vendor not found for Product '{product.title}'")
                continue

            # Check if we've already sent notification for this product/order
            key = (order.oid, product.id)
            if key in sent_notifications:
                log(f"ℹ️ Notification already sent for Product '{product.title}' in order {order.oid}")
                continue

            sent_notifications.add(key)

            log(f"🛍 Product: {product.title}, Vendor: {vendor_user.username}, Vendor ID: {vendor_user.id}")

            # Group name for vendor
            group_name = f"vendor_{vendor_user.id}"
            message = (
                f"Your product '{product.title}' has been paid by a customer!\n"
                f"Customer: {request.user.username}\n"
                f"Amount: {item.total}"
            )
            log(f"🔔 Sending notification to {group_name}: {message}")

            try:
                # Send WebSocket notification
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "vendor_notification",
                        "message": message,
                        "order_id": order.oid,
                        "product_id": product.id,
                        "amount": float(item.total),
                    }
                )

                log(f"✅ Notification sent to {group_name}")
            except Exception as e:
                log(f"❌ Failed to send WebSocket notification for {group_name}: {e}")

    else:
        cart_items_qs = CartOrderProducts.objects.filter(order=order)
        log("ℹ️ Payment was already marked as done, skipping notifications")

    # Prepare template context
    cart_data = {}
    cart_total_amount = 0
    for item in cart_items_qs:
        cart_data[item.id] = {
            "title": item.item,
            "price": item.price,
            "qty": item.qty,
            "total": item.total,
            "image": item.image,
            "vendor_confirmation": item.vendor_confirmation,
        }
        cart_total_amount += item.total

    log(f"🧾 Total cart amount: {cart_total_amount}")

    return render(request, "core/payment-completed.html", {
        "order": order,
        "cart_data": cart_data,
        "cart_total_amount": cart_total_amount,
    })

@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')


@login_required
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)


    orders = CartOrder.objects.annotate(month=ExtractMonth("order_date")).values("month").annotate(count=Count("id")).values("month", "count")
    month = []
    total_orders = []

    for i in orders:
        month.append(calendar.month_name[i["month"]])
        total_orders.append(i["count"])

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, "Address Added Successfully.")
        return redirect("core:dashboard")
    else:
        print("Error")
    
    user_profile = Profile.objects.get(user=request.user)
    print("user profile is: #########################",  user_profile)

    context = {
        "user_profile": user_profile,
        "orders": orders,
        "orders_list": orders_list,
        "address": address,
        "month": month,
        "total_orders": total_orders,
    }
    return render(request, 'core/dashboard.html', context)

def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderProducts.objects.filter(order=order)

    
    context = {
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})

@login_required
def wishlist_view(request):
    wishlist = wishlist_model.objects.all()
    context = {
        "w":wishlist
    }
    return render(request, "core/wishlist.html", context)


    # w

def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)
    print("product id isssssssssssss:" + product_id)

    context = {}

    wishlist_count = wishlist_model.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = wishlist_model.objects.create(
            user=request.user,
            product=product,
        )
        context = {
            "bool": True
        }

    return JsonResponse(context)


# def remove_wishlist(request):
#     pid = request.GET['id']
#     wishlist = wishlist_model.objects.filter(user=request.user).values()

#     product = wishlist_model.objects.get(id=pid)
#     h = product.delete()

#     context = {
#         "bool": True,
#         "wishlist":wishlist
#     }
#     t = render_to_string("core/async/wishlist-list.html", context)
#     return JsonResponse({"data": t, "w":wishlist})

def remove_wishlist(request):
    pid = request.GET['id']
    wishlist = wishlist_model.objects.filter(user=request.user)
    wishlist_d = wishlist_model.objects.get(id=pid)
    delete_product = wishlist_d.delete()
    
    context = {
        "bool":True,
        "w":wishlist
    }
    wishlist_json = serializers.serialize('json', wishlist)
    t = render_to_string('core/async/wishlist-list.html', context)
    return JsonResponse({'data':t,'w':wishlist_json})





# Other Pages 
def contact(request):
    return render(request, "core/contact.html")


def ajax_contact_form(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {
        "bool": True,
        "message": "Message Sent Successfully"
    }

    return JsonResponse({"data":data})


def about_us(request):
    return render(request, "core/about_us.html")

def purchase_guide(request):
    return render(request, "core/purchase_guide.html")

def privacy_policy(request):
    return render(request, "core/privacy_policy.html")

def terms_of_service(request):
    return render(request, "core/terms_of_service.html")


