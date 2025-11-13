from django.urls import path
from . import views

app_name = "lotto"

urlpatterns = [
    path("", views.index, name="index"),
    path("buy/<int:draw_id>/", views.buy, name="buy"),
    path("draw/<int:draw_id>/do/", views.draw_do, name="draw_do"),
    path("draw/<int:draw_id>/result/", views.draw_result, name="draw_result"),
    path("my/orders/", views.my_orders, name="my_orders"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    # ── 판매자(관리자) 리포트 ──
    path("report/draw/<int:draw_id>/", views.report_draw, name="report_draw"),
    path("report/sales/", views.report_sales, name="report_sales"),
    path("report/draw/<int:draw_id>/export.csv", views.report_draw_export_csv, name="report_draw_export_csv"),
    path("draw/<int:draw_id>/rejudge/", views.rejudge_draw, name="rejudge_draw"),

]

