from django.shortcuts import render
from django.http import Http404
from .models import Product

def catalog_list(request):
    products = Product.objects.all().order_by('id')
    context = {
        'title': 'Каталог товаров',
        'products': products
    }
    return render(request, 'catalog/catalog_list.html', context)

def product_detail(request, product_id):
    try:
            # Пытаемся достать товар по ID
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # ЯВНО передаем текст. Если этого не сделать, exception будет пустым!
        raise Http404(f"Извините, но товара с ID {product_id} не существует в нашем каталоге.")
            
    context = {
        'title': product.name,  
        'product': product
    }
    return render(request, 'catalog/product_detail.html', context)

def category_detail(request, category_slug):
    context = {
        'title': f'Категория {category_slug}',
        'category_slug': category_slug
    }
    return render(request, 'catalog/category_detail.html', context)

