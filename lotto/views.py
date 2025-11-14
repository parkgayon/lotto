from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db import transaction
from django.db.models import Count, Sum
from django.http import HttpResponse
from .models import Draw, Order
from .services import gen_auto_numbers, judge, parse_numbers
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from .models import Draw, Order
from .services import judge

from django.contrib.auth import logout as auth_logout   
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from .models import Draw, Order
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Draw, Order


def index(request):
    ctx = {
        "current": Draw.objects.filter(is_closed=False).order_by("-id").first(),
        "last":    Draw.objects.filter(is_closed=True).order_by("-id").first(),
    }
    return render(request, "lotto/index.html", ctx)

@login_required
def buy(request, draw_id):
    draw = get_object_or_404(Draw, id=draw_id, is_closed=False)
    if request.method == "POST":
        mode = request.POST.get("mode")  # 'auto' or 'manual'
        if mode == "auto":
            nums = gen_auto_numbers()
            is_auto = True
        else:
            nums = ",".join(map(str, parse_numbers(request.POST.get("numbers", ""))))
            is_auto = False
        Order.objects.create(user=request.user, draw=draw, numbers=nums, is_auto=is_auto)
        return redirect("lotto:my_orders")
    return render(request, "lotto/buy.html", {"draw": draw})

@staff_member_required
@transaction.atomic
def draw_do(request, draw_id):
    draw = get_object_or_404(Draw, id=draw_id, is_closed=False)
    if not draw.numbers:
        draw.numbers = gen_auto_numbers()
    draw.is_closed = True
    draw.save()

    orders = Order.objects.select_for_update().filter(draw=draw)
    for o in orders:
        rank, matched, prize = judge(draw.numbers, o.numbers)
        o.rank, o.matched, o.prize = rank, matched, prize
        o.save(update_fields=["rank", "matched", "prize"])
    return redirect("lotto:draw_result", draw_id=draw.id)

def draw_result(request, draw_id):
    draw = get_object_or_404(Draw, id=draw_id)
    orders = Order.objects.filter(draw=draw).order_by("rank", "-matched", "id")
    return render(request, "lotto/draw_result.html", {"draw": draw, "orders": orders})

@login_required
def my_orders(request):
    qs = Order.objects.select_related("draw").filter(user=request.user).order_by("-id")
    return render(request, "lotto/my_orders.html", {"orders": qs})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("lotto:index")
    else:
        form = UserCreationForm()
    return render(request, "lotto/signup.html", {"form": form})

# ─────────────────────────────
#      판매자(관리자) 리포트
# ─────────────────────────────
@staff_member_required
def report_draw(request, draw_id):
    draw = get_object_or_404(Draw, id=draw_id)
    qs = Order.objects.filter(draw=draw)

    # 등수별/자동여부별 집계
    by_rank = qs.values("rank").annotate(cnt=Count("id"), sum_prize=Sum("prize")).order_by("rank")
    by_auto = qs.values("is_auto").annotate(cnt=Count("id")).order_by("is_auto")

    total_cnt = qs.count()
    total_prize = qs.aggregate(s=Sum("prize"))["s"] or 0

    ctx = {
        "draw": draw,
        "total_cnt": total_cnt,
        "total_prize": total_prize,
        "by_rank": by_rank,   # rank: 1/2/3/None
        "by_auto": by_auto,   # is_auto: True/False
    }
    return render(request, "lotto/report_draw.html", ctx)

@staff_member_required
def report_sales(request):
    # 최근 10개 회차 요약
    draws = (Draw.objects
             .order_by("-id")[:10])
    rows = []
    for d in draws:
        qs = Order.objects.filter(draw=d)
        rows.append({
            "draw": d,
            "orders": qs.count(),
            "winners": qs.filter(rank__isnull=False).count(),
            "sum_prize": qs.aggregate(s=Sum("prize"))["s"] or 0,
        })
    return render(request, "lotto/report_sales.html", {"rows": rows})

@staff_member_required
def report_draw_export_csv(request, draw_id):
    draw = get_object_or_404(Draw, id=draw_id)
    qs = (Order.objects
          .select_related("user")
          .filter(draw=draw)
          .order_by("rank", "-matched", "id"))

    # CSV 생성
    lines = ["order_id,username,numbers,matched,rank,prize"]
    for o in qs:
        lines.append(f"{o.id},{o.user.username},{o.numbers},{o.matched or ''},{o.rank or ''},{o.prize or ''}")
    csv_data = "\n".join(lines)

    resp = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="draw_{draw.id}_report.csv"'
    return resp

def logout_view(request):
    auth_logout(request)                 
    return redirect("lotto:index")       


@staff_member_required
@transaction.atomic
def rejudge_draw(request, draw_id):
    draw = get_object_or_404(Draw, id=draw_id)
    qs = Order.objects.select_for_update().filter(draw=draw)
    for o in qs:
        rank, matched, prize = judge(draw.numbers, o.numbers)
        o.rank, o.matched, o.prize = rank, matched, prize
        o.save(update_fields=["rank", "matched", "prize"])
    return redirect("lotto:draw_result", draw_id=draw.id)

@staff_member_required
def winners_draw(request, pk):
    draw = get_object_or_404(Draw, pk=pk)

    winners = (
        Order.objects
        .filter(draw=draw, prize__gt=0)
        .select_related("user")
        .order_by("rank", "-prize", "-matched", "id")
    )
    return render(
        request,
        "lotto/winners_draw.html",    
        {"draw": draw, "orders": winners},
    )

