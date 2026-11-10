from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_list, name='catalog_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
]