from django.contrib import admin
from django.urls import path
from myportofolio.views import landing_page  # Pastikan fungsi view-mu terpanggil dengan benar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing_page'),  # Ini wajib ada agar root URL mengarah ke portofoliomu
]