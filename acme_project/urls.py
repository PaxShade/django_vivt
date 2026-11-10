from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('catalog/', include('catalog.urls')),
]

handler404 = 'pages.views.custom_page_not_found'