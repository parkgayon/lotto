from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

def normalize_numbers(s: str) -> str:
    import re
    nums = [int(x) for x in re.findall(r"\d+", s)]
    nums = sorted(set(nums))
    if len(nums) != 6 or any(n < 1 or n > 45 for n in nums):
        raise ValidationError("번호는 1~45 사이의 서로 다른 6개여야 합니다.")
    return ",".join(str(n) for n in nums)

def validate_numbers(value: str):
    normalize_numbers(value)

class Draw(models.Model):
    name = models.CharField("회차명", max_length=50, unique=True)
    open_at = models.DateTimeField("판매 시작", auto_now_add=True)
    close_at = models.DateTimeField("판매 마감", null=True, blank=True)
    numbers = models.CharField("당첨번호(6개)", max_length=50, validators=[validate_numbers], blank=True, default="")
    is_closed = models.BooleanField("마감", default=False)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE, related_name="orders")
    numbers = models.CharField("선택번호(6개)", max_length=50, validators=[validate_numbers])
    is_auto = models.BooleanField("자동", default=False)

    rank = models.PositiveSmallIntegerField("등수", null=True, blank=True)   # 1~3 또는 None
    prize = models.PositiveIntegerField("상금", null=True, blank=True)
    matched = models.PositiveSmallIntegerField("일치개수", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["draw", "user"])]
        ordering = ["-id"]

    def clean(self):
        self.numbers = normalize_numbers(self.numbers)

    def __str__(self):
        return f"#{self.id} {self.user} {self.draw} ({self.numbers})"
