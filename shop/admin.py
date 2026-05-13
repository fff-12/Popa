from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem, ProductRating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'in_stock', 'rating', 'rating_count', 'created_at')
    search_fields = ('name',)
    list_filter = ('category', 'in_stock')
    readonly_fields = ('rating', 'rating_count')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'newsletter', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('newsletter',)
    list_editable = ('newsletter',)


class OrderItemInline(admin.TabularInline):
    """Позиції замовлення відображаються прямо всередині картки замовлення."""
    model = OrderItem
    extra = 0
    readonly_fields = ('name', 'price', 'quantity', 'subtotal', 'product')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone',
                    'delivery_method', 'payment_method', 'total', 'status', 'created_at')
    list_filter = ('status', 'delivery_method', 'payment_method', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_editable = ('status',)     # статус можна змінювати прямо зі списку
    readonly_fields = ('subtotal', 'total', 'delivery_cost', 'created_at', 'paypal_order_id')
    inlines = [OrderItemInline]     # позиції показуються всередині замовлення


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'reviewer_name', 'email', 'rating', 'created_at')
    search_fields = ('reviewer_name', 'email', 'product__name')
    list_filter = ('rating', 'product')
    readonly_fields = ('created_at',)
