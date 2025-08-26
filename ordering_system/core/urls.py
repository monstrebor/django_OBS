from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path("login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("user-login/", views.user_login, name="user-login"),
    path("logout/", views.user_logout, name="logout"),
    path('accounts/register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<int:bill_id>/', views.invoice, name='invoice'),
]