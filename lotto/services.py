import random
from typing import Tuple
from .models import normalize_numbers

def gen_auto_numbers() -> str:
    nums = sorted(random.sample(range(1, 46), 6))
    return ",".join(map(str, nums))

def parse_numbers(s: str) -> list[int]:
    return [int(x) for x in normalize_numbers(s).split(",")]

PRIZE_TABLE = {1: 2_000_000_000, 2: 50_000_000, 3: 1_000_000}

def judge(win_numbers: str, pick_numbers: str) -> Tuple[int | None, int, int]:
    w, p = set(parse_numbers(win_numbers)), set(parse_numbers(pick_numbers))
    m = len(w & p)
    if   m == 6: rank = 1
    elif m == 5: rank = 2
    elif m == 4: rank = 3
    else:        rank = None
    return rank, m, PRIZE_TABLE.get(rank, 0)
