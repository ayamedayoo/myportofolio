from django.contrib import admin
from django.urls import path
from myportofolio import views  # Mengimpor file views dari folder utama

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing_page'),  # Mengarahkan rute utama ke fungsi landing_page
]