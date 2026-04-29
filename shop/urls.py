from django.urls import path
from . import views

urlpatterns = [
    # Основні сторінки
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),

    # ЛАБ 7: кошик
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # ЛАБ 7: підписка на розсилку
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
