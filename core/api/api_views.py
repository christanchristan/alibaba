from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.db.models import Avg, Count
from django.db.models.functions import ExtractMonth
import requests, uuid, json, calendar

from core.models import (
    Product, Category, Vendor, CartOrder, CartOrderProducts,
    ProductReview, wishlist_model, Address, Coupon
)
from core.api.serializers import (
    ProductSerializer, CategorySerializer, VendorSerializer,
    CartOrderSerializer, CartOrderProductsSerializer, ProductReviewSerializer,
    WishlistSerializer, AddressSerializer
)
from userauths.models import Profile, User, ContactUs

import stripe
from paypal.standard.forms import PayPalPaymentsForm


# ----------------- PRODUCT / CATEGORY / VENDOR -----------------

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(product_status="published").order_by("-id")
    serializer_class = ProductSerializer

    @action(detail=False, methods=["get"])
    def featured(self, request):
        products = Product.objects.filter(product_status="published", featured=True).order_by("-id")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = ProductReview.objects.filter(product=product).order_by("-date")
        avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"]
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response({"reviews": serializer.data, "average_rating": avg_rating})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category, product_status="published")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        vendor = self.get_object()
        products = Product.objects.filter(vendor=vendor, product_status="published")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


# ----------------- PRODUCT REVIEW -----------------

class ProductReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        review = ProductReview.objects.create(
            user=request.user,
            product=product,
            review=request.data.get("review"),
            rating=request.data.get("rating"),
        )
        avg_rating = ProductReview.objects.filter(product=product).aggregate(Avg("rating"))["rating__avg"]
        serializer = ProductReviewSerializer(review)
        return Response({"review": serializer.data, "average_rating": avg_rating})


# ----------------- SEARCH / FILTER -----------------

class SearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "")
        products = Product.objects.filter(title__icontains=query).order_by("-date")
        serializer = ProductSerializer(products, many=True)
        return Response({"query": query, "products": serializer.data})


class FilterProductAPIView(APIView):
    def get(self, request):
        categories = request.GET.getlist("category[]")
        vendors = request.GET.getlist("vendor[]")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        products = Product.objects.filter(product_status="published").order_by("-id")

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if categories:
            products = products.filter(category__id__in=categories)
        if vendors:
            products = products.filter(vendor__id__in=vendors)

        serializer = ProductSerializer(products.distinct(), many=True)
        return Response(serializer.data)


# ----------------- CART API -----------------

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = CartOrderProducts.objects.filter(order__user=request.user, order__paid_status=False)
        serializer = CartOrderProductsSerializer(cart_items, many=True)
        total_amount = sum([item.total for item in cart_items])
        return Response({"cart_items": serializer.data, "total_amount": total_amount})

    def post(self, request):
        product_id = request.data.get("product_id")
        qty = int(request.data.get("quantity", 1))
        product = get_object_or_404(Product, pk=product_id)

        order, created = CartOrder.objects.get_or_create(user=request.user, paid_status=False, defaults={"price": 0})
        cart_item, item_created = CartOrderProducts.objects.get_or_create(order=order, item=product.title, defaults={
            "qty": qty,
            "price": product.price,
            "total": product.price * qty
        })
        if not item_created:
            cart_item.qty += qty
            cart_item.total = cart_item.qty * cart_item.price
            cart_item.save()
        order.price = sum([item.total for item in order.cartorderproducts_set.all()])
        order.save()

        serializer = CartOrderProductsSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        item_id = request.data.get("item_id")
        qty = int(request.data.get("quantity"))
        cart_item = get_object_or_404(CartOrderProducts, pk=item_id, order__user=request.user, order__paid_status=False)
        cart_item.qty = qty
        cart_item.total = qty * cart_item.price
        cart_item.save()
        return Response({"message": "Cart updated"})


    def delete(self, request):
        item_id = request.data.get("item_id")
        cart_item = get_object_or_404(CartOrderProducts, pk=item_id, order__user=request.user, order__paid_status=False)
        cart_item.delete()
        return Response({"message": "Item deleted"})


# ----------------- CHECKOUT / PAYMENT -----------------

class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(CartOrder, oid=order_id, user=request.user)
        order_items = CartOrderProducts.objects.filter(order=order)
        serializer = CartOrderProductsSerializer(order_items, many=True)
        return Response({
            "order": CartOrderSerializer(order).data,
            "items": serializer.data,
            "stripe_publishable_key": settings.STRIPE_PUBLIC_KEY
        })


class StripeCheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(CartOrder, oid=order_id, user=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.create(
            customer_email=order.email,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "USD",
                    "product_data": {"name": order.full_name},
                    "unit_amount": int(order.price * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid])),
            cancel_url=request.build_absolute_uri(reverse("core:payment-failed"))
        )

        order.stripe_payment_intent = checkout_session["id"]
        order.save()
        return Response({"sessionId": checkout_session.id})


# ----------------- WISHLIST API -----------------

class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist = wishlist_model.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product_id")
        product = get_object_or_404(Product, pk=product_id)
        wishlist_model.objects.get_or_create(user=request.user, product=product)
        return Response({"message": "Added to wishlist"})

    def delete(self, request):
        product_id = request.data.get("product_id")
        wishlist_item = get_object_or_404(wishlist_model, user=request.user, product_id=product_id)
        wishlist_item.delete()
        return Response({"message": "Removed from wishlist"})


# ----------------- CONTACT -----------------

class ContactAPIView(APIView):
    def post(self, request):
        contact = ContactUs.objects.create(
            full_name=request.data.get("full_name"),
            email=request.data.get("email"),
            phone=request.data.get("phone"),
            subject=request.data.get("subject"),
            message=request.data.get("message")
        )
        return Response({"message": "Message sent successfully"})
