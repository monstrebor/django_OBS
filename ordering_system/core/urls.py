from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path("login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("user-login/", views.user_login, name="user-login"),
    path("logout/", views.user_logout, name="logout"),
    path('accounts/register/', views.register, name='register'),
    
    path("product_list/", views.product_list, name="product-list"),
    path("product_create/", views.product_create, name="product-create"),
    path("product_update/<int:product_id>/", views.product_update, name="product-update"),
    path("product_delete/<int:product_id>/", views.product_delete, name="product-delete"),
    
    path("products/", views.view_product, name="view-product"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<int:bill_id>/', views.invoice, name='invoice'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)