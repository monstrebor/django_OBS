from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('accounts/login/', LoginView.as_view(), name='login'),  # Remove template_name
    path('accounts/register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<int:bill_id>/', views.invoice, name='invoice'),
]