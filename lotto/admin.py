from django.contrib import admin
from .models import Draw, Order

# ===== 추첨 회차(Draw) Admin 설정 =====
@admin.register(Draw)
class DrawAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_closed", "numbers", "open_at", "close_at")
    search_fields = ("name",)
    list_filter = ("is_closed",)

# ===== 주문/응모(Order) Admin 설정 =====
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "draw", "numbers", "is_auto", "matched", "rank", "prize", "created_at")
    list_filter = ("is_auto", "rank")
    search_fields = ("user__username", "numbers")
