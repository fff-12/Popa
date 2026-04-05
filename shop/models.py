from django.db import models

# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Назва")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    
    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']
        
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    # ЗМІНА #1: Додано поле photo для закладення фотографій товарів
    # upload_to='products/' - автоматично зберігає фото в папку media/products/
    # blank=True, null=True - фото не обов'язкове
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Назва")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    # ForeignKey до Category - це дозволяє фільтрувати товари по категоріях
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категорія")
    photo = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото")  # НОВЕ ПОЛЕ
    in_stock = models.BooleanField(default=True, verbose_name="В наявності")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Ім'я")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    cart = models.ManyToManyField(Product, blank=True, related_name='customers', verbose_name="Кошик")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    
    class Meta: 
        verbose_name = "Клієнт"
        verbose_name_plural = "Клієнти"
        ordering = ['name']

    def __str__(self):
        return self.name