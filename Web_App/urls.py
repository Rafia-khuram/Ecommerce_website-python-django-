from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path("", views.index, name='index'),
   path("products/<str:category>/", views.products, name='products'),
   path("product_detail/<str:pk>/", views.product_detail, name = 'product_detail'),
   path("register", views.register, name='register'),
   path("login_user", views.login_user, name='login_user'),
   path("logout_user", views.logout_user, name='logout_user'),
   path("view_transactions/<str:customer_id>/", views.view_transactions, name='view_transactions'),
   path("cart", views.cart, name='cart'),
   path("checkout", views.checkout, name='checkout'),
   path("update_item", views.update_item, name="update_item"),
   path("process_order/<str:order_id>/", views.process_order, name="process_order"),
   path("load_data", views.load_data, name='load_data'),
   path("payment/<str:order_id>/", views.payment, name="payment"),
   path("payment_success", views.payment_success, name='payment_success'),
   path("payment_cancel", views.payment_cancel, name="payment_cancel"),
   path("webhooks/stripe", views.stripe_webhook, name="stripe_webhook")

]