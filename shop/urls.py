from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    # ЗМІНА #4: Додано маршрут для детальної сторінки товару
    # <int:product_id> - захоплює ID товару з URL (наприклад: /product/1/)
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),
]