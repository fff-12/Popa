from django.urls import path
from . import views

urlpatterns = [
    # Основні сторінки
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),

    # Кошик
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Оформлення замовлення
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),

    # Підписка на розсилку
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
<<<<<<< HEAD

    # ── ЛАБ 8: Авторизація ──
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('cabinet/',  views.cabinet,       name='cabinet'),
    path('password-reset/',        views.password_reset_request, name='password_reset'),
    path('password-reset/verify/', views.password_reset_verify,  name='password_reset_verify'),

    # ── Адміністраторський функціонал ──
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Товари
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/product/new/', views.admin_product_edit, name='admin_product_new'),
    path('admin/product/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/product/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
    
    # Категорії
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/category/new/', views.admin_category_edit, name='admin_category_new'),
    path('admin/category/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/category/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Замовлення
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
=======
>>>>>>> 8c07882ba6a20f6962f51229330b4e18560393d8
]
