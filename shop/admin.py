from django.contrib import admin
from .models import Category, Product, Customer
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'price', 'category', 'in_stock', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('category', 'in_stock', 'created_at', 'updated_at')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'cart_count', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at', 'updated_at')
    
    def cart_count(self, obj):
        return obj.cart.count() 
    cart_count.short_description = 'Кількість товарів у кошику'