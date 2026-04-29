from django.contrib import admin
from .models import Category, Product, Customer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # ЛАБ 7: додано колонки rating та rating_count у список товарів адміна
    list_display = ('id', 'name', 'price', 'category', 'in_stock',
                    'rating', 'rating_count', 'created_at')
    search_fields = ('name',)
    list_filter = ('category', 'in_stock', 'created_at')
    # rating і rating_count відображаємо як readonly — вони оновлюються через сайт
    readonly_fields = ('rating', 'rating_count')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # ЛАБ 7: додано поле newsletter у список клієнтів
    list_display = ('id', 'name', 'email', 'phone', 'newsletter', 'cart_count', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('newsletter', 'created_at')
    # newsletter можна перемикати прямо зі списку
    list_editable = ('newsletter',)

    def cart_count(self, obj):
        return obj.cart.count()
    cart_count.short_description = 'Товарів у кошику'
