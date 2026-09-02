from django.contrib import admin
from django.urls import path
from myportofolio import views  # Pastikan mengarah ke file views yang benar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing_page'),  # Jalur utama ('') wajib ada
]