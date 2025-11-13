# config/urls.py
from django.contrib import admin
from django.urls import path, include
from lotto import views as lotto_views  # ¡ç Ãß°¡

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    path("logout/", lotto_views.logout_view, name="logout"),       
    path("accounts/logout/", lotto_views.logout_view),            
    path("", include("lotto.urls")),
]
