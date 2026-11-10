from django.contrib import admin
from .models import Product
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available')  # Выведет удобную таблицу в админке
    list_filter = ('is_available',)                 # Добавит фильтрацию по наличию
    search_fields = ('name', 'description')          # Добавит поиск по названию и описанию