"""
IKMC Math Practice – Backend v3
Dynamic question generation per grade (1-5), student profiles,
3-month progress tracking, voucher system.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import random, json, os, math
from datetime import datetime, date
from functools import partial

app = Flask(__name__)
CORS(app, origins=["https://ikmc.vercel.app", "http://localhost:3000"])

DATA_DIR = os.path.dirname(__file__)
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")

# ─────────────────────────────────────────────
#  PERSISTENT DATA HELPERS
# ─────────────────────────────────────────────

def load_students():
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_students(data):
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
#  DYNAMIC QUESTION GENERATOR
#  Follows IKMC curriculum per grade
# ─────────────────────────────────────────────

def make_id():
    return random.randint(100000, 999999)

def _wrongs_near(ans, lo, hi):
    ans_int = int(ans) if isinstance(ans, (int, float)) else ans
    wrongs = set()
    attempts = 0
    while len(wrongs) < 3 and attempts < 200:
        attempts += 1
        delta = random.choice([-3, -2, -1, 1, 2, 3, 4, 5, -4, -5])
        cand = ans_int + delta
        if lo <= cand <= hi and cand != ans_int:
            wrongs.add(str(cand))
    while len(wrongs) < 3:
        cand = random.randint(max(lo, ans_int - 10), min(hi, ans_int + 10))
        if str(cand) != str(ans_int):
            wrongs.add(str(cand))
    return list(wrongs)

def _shuffle_opts(correct, wrongs):
    pool = [correct] + wrongs[:3]
    random.shuffle(pool)
    return pool[:4]

def _make_q_d(difficulty, expr, ans, wrong, topic):
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": difficulty,
            "question_en": f"What is {expr}?", "question_vi": f"{expr} bằng bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{expr} = {ans}.", "explanation_vi": f"{expr} = {ans}.",
            "topic": topic}


# ── GRADE 1 ──────────────────────────────────
def gen_g1_addition(d="easy"):
    if d == "easy":   a, b = random.randint(1, 10), random.randint(1, 10)
    elif d == "medium": a, b = random.randint(5, 20), random.randint(5, 20)
    else:             a, b = random.randint(10, 50), random.randint(10, 50)
    ans = a + b
    wrong = _wrongs_near(ans, 1, ans + 10)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"What is {a} + {b}?", "question_vi": f"{a} + {b} bằng bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{a} + {b} = {ans}.", "explanation_vi": f"{a} + {b} = {ans}.",
            "topic": "addition"}

def gen_g1_subtraction(d="easy"):
    hi = {"easy": 10, "medium": 20, "hard": 50}[d]
    b = random.randint(1, hi // 2)
    a = random.randint(b, hi)
    ans = a - b
    wrong = _wrongs_near(ans, 0, hi)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"What is {a} − {b}?", "question_vi": f"{a} − {b} bằng bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{a} − {b} = {ans}.", "explanation_vi": f"{a} − {b} = {ans}.",
            "topic": "subtraction"}

def gen_g1_sequence(d="easy"):
    if d == "easy":   step, start = random.choice([1, 2]), random.randint(1, 8)
    elif d == "medium": step, start = random.choice([2, 3, 5]), random.randint(1, 10)
    else:             step, start = random.choice([4, 5, 10]), random.randint(1, 20)
    seq = [start + i * step for i in range(6)]
    pos = random.randint(1, 4)
    ans = seq[pos]
    display = [str(x) if i != pos else "__" for i, x in enumerate(seq)]
    wrong = _wrongs_near(ans, 1, max(seq) + 10)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Find the missing number: {', '.join(display)}",
            "question_vi": f"Tìm số còn thiếu: {', '.join(display)}",
            "options": opts, "answer": str(ans),
            "explanation_en": f"Pattern: +{step} each step. Answer: {ans}.",
            "explanation_vi": f"Quy luật cộng {step}. Đáp án: {ans}.", "topic": "patterns"}

def gen_g1_comparison(d="easy"):
    hi = {"easy": 15, "medium": 30, "hard": 100}[d]
    a, b = random.sample(range(1, hi), 2)
    bigger = max(a, b)
    wrong = _wrongs_near(bigger, 1, hi)
    opts = _shuffle_opts(str(bigger), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Which is larger: {a} or {b}?", "question_vi": f"Số nào lớn hơn: {a} hay {b}?",
            "options": opts, "answer": str(bigger),
            "explanation_en": f"{bigger} > {min(a, b)}.", "explanation_vi": f"{bigger} > {min(a, b)}.",
            "topic": "comparison"}

def gen_g1_word_problem(d="easy"):
    if d == "easy":   a, b = random.randint(2, 8), random.randint(1, 5)
    elif d == "medium": a, b = random.randint(5, 15), random.randint(2, 8)
    else:             a, b = random.randint(10, 30), random.randint(5, 15)
    op = random.choice(["+", "-"])
    if op == "+":
        ans = a + b
        en = f"There are {a} apples. {b} more are added. How many now?"
        vi = f"Có {a} quả táo. Thêm {b} quả. Bây giờ có bao nhiêu?"
        exp_en, exp_vi = f"{a} + {b} = {ans}.", f"{a} + {b} = {ans}."
    else:
        ans = a - b
        en = f"There are {a} birds. {b} fly away. How many remain?"
        vi = f"Có {a} con chim. {b} con bay đi. Còn lại bao nhiêu?"
        exp_en, exp_vi = f"{a} − {b} = {ans}.", f"{a} − {b} = {ans}."
    wrong = _wrongs_near(ans, 0, a + b + 5)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": en, "question_vi": vi, "options": opts, "answer": str(ans),
            "explanation_en": exp_en, "explanation_vi": exp_vi, "topic": "word_problems"}


# ── GRADE 2 ──────────────────────────────────
def gen_g2_addition(d="medium"):
    if d == "easy":   a, b = random.randint(1, 30), random.randint(1, 30)
    elif d == "medium": a, b = random.randint(10, 50), random.randint(10, 50)
    else:             a, b = random.randint(50, 200), random.randint(50, 200)
    ans = a + b
    wrong = _wrongs_near(ans, 1, ans + 20)
    return _make_q_d(d, f"{a} + {b}", ans, wrong, "addition")

def gen_g2_multiplication(d="medium"):
    if d == "easy":   a, b = random.randint(2, 3), random.randint(2, 5)
    elif d == "medium": a, b = random.randint(2, 5), random.randint(2, 9)
    else:             a, b = random.randint(5, 9), random.randint(5, 9)
    ans = a * b
    wrong = _wrongs_near(ans, 2, ans + 20)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"What is {a} × {b}?", "question_vi": f"{a} × {b} bằng bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{a} × {b} = {ans}.", "explanation_vi": f"{a} × {b} = {ans}.",
            "topic": "multiplication"}

def gen_g2_missing_number(d="medium"):
    if d == "easy":   a, b = random.randint(2, 15), random.randint(1, 10)
    elif d == "medium": a, b = random.randint(5, 30), random.randint(1, 20)
    else:             a, b = random.randint(20, 80), random.randint(10, 50)
    total = a + b
    side = random.choice(["left", "right"])
    res = a if side == "left" else b
    en = f"■ + {b} = {total}. What is ■?" if side == "left" else f"{a} + ■ = {total}. What is ■?"
    vi = f"■ + {b} = {total}. ■ bằng bao nhiêu?" if side == "left" else f"{a} + ■ = {total}. ■ bằng bao nhiêu?"
    wrong = _wrongs_near(res, 1, total)
    opts = _shuffle_opts(str(res), wrong)
    return {"id": make_id(), "level": d,
            "question_en": en, "question_vi": vi, "options": opts, "answer": str(res),
            "explanation_en": f"■ = {total} − {b if side=='left' else a} = {res}.",
            "explanation_vi": f"■ = {res}.", "topic": "missing_number"}

def gen_g2_geometry(d="medium"):
    shapes = [{"name_en": "triangle", "name_vi": "tam giác", "sides": 3},
              {"name_en": "square",   "name_vi": "hình vuông", "sides": 4},
              {"name_en": "pentagon", "name_vi": "ngũ giác",  "sides": 5},
              {"name_en": "hexagon",  "name_vi": "lục giác",  "sides": 6}]
    count = {"easy": random.randint(1, 2), "medium": random.randint(2, 4), "hard": random.randint(3, 6)}[d]
    sh = random.choice(shapes)
    ans = sh["sides"] * count
    wrong = _wrongs_near(ans, 2, 40)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"How many sides do {count} {sh['name_en']}s have in total?",
            "question_vi": f"{count} {sh['name_vi']} có tổng cộng bao nhiêu cạnh?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{count} × {sh['sides']} = {ans}.",
            "explanation_vi": f"{count} × {sh['sides']} = {ans}.", "topic": "geometry"}

def gen_g2_word_problem(d="medium"):
    items = random.choice(["pencils", "books", "candies", "marbles", "stickers"])
    items_vi = {"pencils": "bút chì", "books": "quyển sách", "candies": "kẹo",
                "marbles": "viên bi", "stickers": "nhãn dán"}[items]
    if d == "easy":   bags, each = random.randint(2, 3), random.randint(2, 5)
    elif d == "medium": bags, each = random.randint(2, 5), random.randint(3, 8)
    else:             bags, each = random.randint(4, 8), random.randint(5, 12)
    give = random.randint(1, bags * each - 1)
    total = bags * each
    ans = total - give
    wrong = _wrongs_near(ans, 1, total)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Sam has {bags} bags with {each} {items} each. He gives away {give}. How many left?",
            "question_vi": f"Sam có {bags} túi, mỗi túi {each} {items_vi}. Cho đi {give}. Còn lại bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{bags}×{each}={total}. {total}−{give}={ans}.",
            "explanation_vi": f"{bags}×{each}={total}. {total}−{give}={ans}.", "topic": "word_problems"}


# ── GRADE 3 ──────────────────────────────────
def gen_g3_multiplication(d="medium"):
    if d == "easy":   a, b = random.randint(2, 8), random.randint(2, 8)
    elif d == "medium": a, b = random.randint(6, 12), random.randint(6, 12)
    else:             a, b = random.randint(12, 20), random.randint(12, 20)
    ans = a * b
    wrong = _wrongs_near(ans, max(4, ans - 30), ans + 30)
    return _make_q_d(d, f"{a} × {b}", ans, wrong, "multiplication")

def gen_g3_division(d="medium"):
    if d == "easy":   b, ans_hi = random.randint(2, 5), 8
    elif d == "medium": b, ans_hi = random.randint(2, 9), 12
    else:             b, ans_hi = random.randint(6, 12), 20
    ans = random.randint(2, ans_hi)
    a = b * ans
    wrong = _wrongs_near(ans, 1, ans_hi + 5)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"What is {a} ÷ {b}?", "question_vi": f"{a} ÷ {b} bằng bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{a} ÷ {b} = {ans}.", "explanation_vi": f"{a} ÷ {b} = {ans}.",
            "topic": "division"}

def gen_g3_fractions(d="medium"):
    if d == "easy":   denom = random.choice([2, 4])
    elif d == "medium": denom = random.choice([2, 4, 5, 10])
    else:             denom = random.choice([3, 6, 8, 10])
    numer = random.randint(1, denom - 1)
    total = denom * random.randint(2, 6)
    ans = (total * numer) // denom
    wrong = _wrongs_near(ans, 1, total)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"What is {numer}/{denom} of {total}?",
            "question_vi": f"{numer}/{denom} của {total} bằng bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{total}÷{denom}×{numer}={ans}.", "explanation_vi": f"{total}÷{denom}×{numer}={ans}.",
            "topic": "fractions"}

def gen_g3_perimeter(d="medium"):
    shape = "square" if d == "easy" else random.choice(["square", "rectangle", "triangle"])
    s_hi = {"easy": 8, "medium": 12, "hard": 20}[d]
    if shape == "square":
        s = random.randint(3, s_hi); ans = 4 * s
        en, vi = f"Square side {s} cm. Perimeter?", f"Hình vuông cạnh {s} cm. Chu vi?"
        exp_en, exp_vi = f"4×{s}={ans} cm.", f"4×{s}={ans} cm."
    elif shape == "rectangle":
        l = random.randint(4, s_hi); w = random.randint(2, l - 1); ans = 2 * (l + w)
        en, vi = f"Rectangle {l}×{w} cm. Perimeter?", f"Hình chữ nhật {l}×{w} cm. Chu vi?"
        exp_en, exp_vi = f"2×({l}+{w})={ans} cm.", f"2×({l}+{w})={ans} cm."
    else:
        a, b, c = random.randint(3, s_hi), random.randint(3, s_hi), random.randint(3, s_hi); ans = a + b + c
        en, vi = f"Triangle sides {a},{b},{c} cm. Perimeter?", f"Tam giác cạnh {a},{b},{c} cm. Chu vi?"
        exp_en, exp_vi = f"{a}+{b}+{c}={ans} cm.", f"{a}+{b}+{c}={ans} cm."
    wrong = _wrongs_near(ans, 4, ans + 30)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": en, "question_vi": vi, "options": opts, "answer": str(ans),
            "explanation_en": exp_en, "explanation_vi": exp_vi, "topic": "geometry"}

def gen_g3_logic(d="medium"):
    if d == "easy":   a, extra = random.randint(2, 8), random.randint(1, 4)
    elif d == "medium": a, extra = random.randint(5, 15), random.randint(2, 8)
    else:             a, extra = random.randint(10, 30), random.randint(5, 15)
    b = a + extra; total = a + b
    wrong = _wrongs_near(a, 1, total)
    opts = _shuffle_opts(str(a), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Two numbers sum to {total}. One is {extra} more. Smaller number?",
            "question_vi": f"Tổng hai số là {total}. Số này hơn số kia {extra}. Số nhỏ hơn?",
            "options": opts, "answer": str(a),
            "explanation_en": f"2x+{extra}={total} → x={a}.", "explanation_vi": f"2x+{extra}={total} → x={a}.",
            "topic": "logic"}

def gen_g3_word_problem(d="medium"):
    if d == "easy":   price, qty = random.randint(2, 5), random.randint(2, 5)
    elif d == "medium": price, qty = random.randint(3, 9), random.randint(3, 8)
    else:             price, qty = random.randint(5, 15), random.randint(5, 12)
    paid = price * qty + random.randint(1, 3) * price
    total_cost = price * qty; change = paid - total_cost
    wrong = _wrongs_near(change, 1, paid)
    opts = _shuffle_opts(str(change), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Notebook costs {price} coins. Buy {qty}, pay {paid}. Change?",
            "question_vi": f"Sách giá {price} xu. Mua {qty} quyển, trả {paid}. Tiền thừa?",
            "options": opts, "answer": str(change),
            "explanation_en": f"{price}×{qty}={total_cost}. {paid}−{total_cost}={change}.",
            "explanation_vi": f"{price}×{qty}={total_cost}. {paid}−{total_cost}={change}.",
            "topic": "word_problems"}


# ── GRADE 4 ──────────────────────────────────
def gen_g4_large_arithmetic(d="medium"):
    ops = [("×", lambda a, b: a * b), ("+", lambda a, b: a + b), ("−", lambda a, b: a - b)]
    sym, fn = random.choice(ops)
    if d == "easy":
        if sym == "×": a, b = random.randint(5, 15), random.randint(5, 15)
        elif sym == "+": a, b = random.randint(50, 200), random.randint(50, 200)
        else: a = random.randint(100, 500); b = random.randint(50, a - 10)
    elif d == "medium":
        if sym == "×": a, b = random.randint(12, 25), random.randint(12, 25)
        elif sym == "+": a, b = random.randint(100, 500), random.randint(100, 500)
        else: a = random.randint(200, 999); b = random.randint(100, a - 50)
    else:
        if sym == "×": a, b = random.randint(20, 50), random.randint(20, 50)
        elif sym == "+": a, b = random.randint(500, 999), random.randint(500, 999)
        else: a = random.randint(500, 9999); b = random.randint(200, a - 100)
    ans = fn(a, b)
    wrong = _wrongs_near(ans, max(1, ans - 100), ans + 100)
    return _make_q_d(d, f"{a} {sym} {b}", ans, wrong, "arithmetic")

def gen_g4_area(d="medium"):
    shape = "square" if d == "easy" else random.choice(["square", "rectangle"])
    s_hi = {"easy": 10, "medium": 15, "hard": 25}[d]
    if shape == "square":
        s = random.randint(4, s_hi); ans = s * s
        en, vi = f"Square side {s} cm. Area?", f"Hình vuông cạnh {s} cm. Diện tích?"
        exp_en, exp_vi = f"{s}²={ans} cm².", f"{s}²={ans} cm²."
    else:
        l = random.randint(5, s_hi); w = random.randint(3, l); ans = l * w
        en, vi = f"Rectangle {l}×{w} cm. Area?", f"Hình chữ nhật {l}×{w} cm. Diện tích?"
        exp_en, exp_vi = f"{l}×{w}={ans} cm².", f"{l}×{w}={ans} cm²."
    wrong = _wrongs_near(ans, 4, ans + 60)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": en, "question_vi": vi, "options": opts, "answer": str(ans),
            "explanation_en": exp_en, "explanation_vi": exp_vi, "topic": "geometry"}

def gen_g4_factors(d="medium"):
    choices = {"easy": [6, 8, 9, 10, 12, 15], "medium": [12, 16, 18, 20, 24, 30, 36],
               "hard": [48, 60, 72, 84, 96, 100, 120]}[d]
    n = random.choice(choices)
    factors = [i for i in range(1, n + 1) if n % i == 0]
    ans = len(factors)
    wrong = _wrongs_near(ans, 1, max(ans + 6, 12))
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"How many factors does {n} have?",
            "question_vi": f"Số {n} có bao nhiêu ước số?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"Factors of {n}: {factors}. Total: {ans}.",
            "explanation_vi": f"Ước của {n}: {factors}. Tổng: {ans}.", "topic": "number_theory"}

def gen_g4_average(d="medium"):
    cnt = {"easy": random.randint(2, 3), "medium": random.randint(3, 5), "hard": random.randint(4, 6)}[d]
    hi = {"easy": 20, "medium": 30, "hard": 50}[d]
    nums = [random.randint(hi // 3, hi) for _ in range(cnt)]
    total = sum(nums); rem = total % cnt
    if rem: nums[0] += cnt - rem; total = sum(nums)
    ans = total // cnt
    wrong = _wrongs_near(ans, 2, hi + 5)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Average of: {', '.join(map(str, nums))}?",
            "question_vi": f"Trung bình của: {', '.join(map(str, nums))}?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"Sum={total}÷{cnt}={ans}.", "explanation_vi": f"Tổng={total}÷{cnt}={ans}.",
            "topic": "statistics"}

def gen_g4_logic(d="medium"):
    if d == "easy":   mul_f, add_l = random.randint(2, 3), random.randint(1, 5)
    elif d == "medium": mul_f, add_l = random.randint(2, 5), random.randint(2, 8)
    else:             mul_f, add_l = random.randint(3, 8), random.randint(5, 15)
    original = random.randint(2, 10)
    result = original * mul_f + add_l
    wrong = _wrongs_near(original, 1, 20)
    opts = _shuffle_opts(str(original), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"A number × {mul_f} then + {add_l} = {result}. Original?",
            "question_vi": f"Số × {mul_f} rồi + {add_l} = {result}. Số ban đầu?",
            "options": opts, "answer": str(original),
            "explanation_en": f"({result}−{add_l})÷{mul_f}={original}.",
            "explanation_vi": f"({result}−{add_l})÷{mul_f}={original}.", "topic": "logic"}

def gen_g4_word_problem(d="medium"):
    if d == "easy":   speed, hours = random.randint(2, 5), random.randint(2, 4)
    elif d == "medium": speed, hours = random.randint(4, 8), random.randint(3, 6)
    else:             speed, hours = random.randint(6, 15), random.randint(4, 8)
    dist = speed * hours
    wrong = _wrongs_near(dist, 2, dist + 20)
    opts = _shuffle_opts(str(dist), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Cyclist goes {speed} km/h for {hours} hours. Distance?",
            "question_vi": f"Xe đạp đi {speed} km/h trong {hours} giờ. Quãng đường?",
            "options": opts, "answer": str(dist),
            "explanation_en": f"{speed}×{hours}={dist} km.", "explanation_vi": f"{speed}×{hours}={dist} km.",
            "topic": "word_problems"}


# ── GRADE 5 ──────────────────────────────────
def gen_g5_percentage(d="medium"):
    if d == "easy":   pct, total = random.choice([10, 50]), random.choice([20, 40, 60, 80, 100])
    elif d == "medium": pct, total = random.choice([10, 20, 25, 50, 75]), random.choice([40, 60, 80, 100, 120, 200])
    else:             pct, total = random.choice([15, 30, 35, 45, 60, 70]), random.choice([60, 80, 120, 150, 200, 240])
    ans = (total * pct) // 100
    wrong = _wrongs_near(ans, 2, total)
    opts = _shuffle_opts(str(ans), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"What is {pct}% of {total}?", "question_vi": f"{pct}% của {total} là bao nhiêu?",
            "options": opts, "answer": str(ans),
            "explanation_en": f"{total}×{pct}/100={ans}.", "explanation_vi": f"{total}×{pct}/100={ans}.",
            "topic": "percentages"}

def gen_g5_ratio(d="medium"):
    if d == "easy":   a, b = 1, random.randint(1, 3)
    elif d == "medium": a, b = random.randint(2, 6), random.randint(2, 6)
    else:             a, b = random.randint(3, 8), random.randint(3, 8)
    total = random.randint(3, 8) * (a + b)
    part_a = (total * a) // (a + b)
    larger = max(part_a, total - part_a)
    wrong = _wrongs_near(larger, 2, total)
    opts = _shuffle_opts(str(larger), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Ratio {a}:{b}, sum={total}. Larger part?",
            "question_vi": f"Tỉ lệ {a}:{b}, tổng={total}. Phần lớn hơn?",
            "options": opts, "answer": str(larger),
            "explanation_en": f"Each unit={total}//{a+b}. Larger={max(a,b)}×{total//(a+b)}={larger}.",
            "explanation_vi": f"Mỗi phần={total//(a+b)}. Lớn hơn={larger}.", "topic": "ratios"}

def gen_g5_prime(d="medium"):
    if d == "easy":
        primes, non_p = [2, 3, 5, 7], [4, 6, 8, 9, 10]
    elif d == "medium":
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        non_p  = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 25, 26, 27, 28]
    else:
        primes = [53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        non_p  = [51, 52, 54, 55, 56, 57, 58, 62, 63, 64, 65, 66, 68, 69, 70]
    target = random.choice(primes)
    wrong = random.sample([x for x in non_p if x != target], 3)
    opts = _shuffle_opts(str(target), [str(x) for x in wrong])
    return {"id": make_id(), "level": d,
            "question_en": "Which number is prime?", "question_vi": "Số nào là số nguyên tố?",
            "options": opts, "answer": str(target),
            "explanation_en": f"{target} is prime (factors: 1 and {target} only).",
            "explanation_vi": f"{target} là số nguyên tố.", "topic": "number_theory"}

def gen_g5_speed_time(d="medium"):
    if d == "easy":   dist, spd = random.choice([20, 30, 40, 50]), random.choice([5, 10])
    elif d == "medium": dist, spd = random.choice([60, 80, 90, 120, 150, 200]), random.choice([30, 40, 50, 60])
    else:             dist, spd = random.choice([150, 180, 200, 240, 300]), random.choice([25, 30, 45, 60])
    time = dist // spd
    wrong = _wrongs_near(time, 1, 12)
    opts = _shuffle_opts(str(time), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Car travels {dist} km at {spd} km/h. Time?",
            "question_vi": f"Ô tô đi {dist} km, tốc độ {spd} km/h. Mất bao nhiêu giờ?",
            "options": opts, "answer": str(time),
            "explanation_en": f"{dist}÷{spd}={time} hours.", "explanation_vi": f"{dist}÷{spd}={time} giờ.",
            "topic": "speed_time"}

def gen_g5_algebra(d="medium"):
    if d == "easy":   m, c = random.randint(2, 4), 0
    elif d == "medium": m, c = random.randint(2, 5), random.randint(1, 10)
    else:             m, c = random.randint(3, 8), random.randint(5, 20)
    x = random.randint(2, 12)
    result = m * x + c
    wrong = _wrongs_near(x, 1, 20)
    opts = _shuffle_opts(str(x), wrong)
    eq = f"{m}x = {result}" if c == 0 else f"{m}x + {c} = {result}"
    return {"id": make_id(), "level": d,
            "question_en": f"Solve: {eq}. x=?", "question_vi": f"Giải: {eq}. x=?",
            "options": opts, "answer": str(x),
            "explanation_en": f"x={x}.", "explanation_vi": f"x={x}.", "topic": "algebra"}

def gen_g5_word_problem(d="medium"):
    if d == "easy":   price, qty, disc = random.randint(2, 8), random.randint(2, 5), 10
    elif d == "medium": price, qty, disc = random.randint(5, 20), random.randint(5, 15), random.choice([10, 20, 25])
    else:             price, qty, disc = random.randint(10, 30), random.randint(8, 20), random.choice([15, 20, 30, 35])
    original = price * qty; discount = (original * disc) // 100; final = original - discount
    wrong = _wrongs_near(final, 5, original)
    opts = _shuffle_opts(str(final), wrong)
    return {"id": make_id(), "level": d,
            "question_en": f"Item {price} coins × {qty} with {disc}% off. Pay?",
            "question_vi": f"Đồ {price} xu × {qty} cái, giảm {disc}%. Phải trả?",
            "options": opts, "answer": str(final),
            "explanation_en": f"{price}×{qty}={original}. Discount={discount}. Pay={final}.",
            "explanation_vi": f"{price}×{qty}={original}. Giảm={discount}. Trả={final}.",
            "topic": "word_problems"}


# ── HELPERS (kept for backward compat) ───────
def _level(grade):
    return {1: "easy", 2: "easy", 3: "medium", 4: "medium", 5: "hard"}[grade]

def _make_q(grade, expr, ans, wrong, topic):
    return _make_q_d(_level(grade), expr, ans, wrong, topic)


# ── QUESTION BANK (100 per grade: 30E/40M/30H) ──
_GRADE_FUNS = {
    1: [gen_g1_addition, gen_g1_subtraction, gen_g1_sequence, gen_g1_comparison, gen_g1_word_problem],
    2: [gen_g2_addition, gen_g2_multiplication, gen_g2_missing_number, gen_g2_geometry, gen_g2_word_problem],
    3: [gen_g3_multiplication, gen_g3_division, gen_g3_fractions, gen_g3_perimeter, gen_g3_logic, gen_g3_word_problem],
    4: [gen_g4_large_arithmetic, gen_g4_area, gen_g4_factors, gen_g4_average, gen_g4_logic, gen_g4_word_problem],
    5: [gen_g5_percentage, gen_g5_ratio, gen_g5_prime, gen_g5_speed_time, gen_g5_algebra, gen_g5_word_problem],
}
BANK_COUNTS = [("easy", 30), ("medium", 40), ("hard", 30)]

BANK_GENERATORS = {
    g: {d: [partial(fn, d) for fn in fns] for d, _ in BANK_COUNTS}
    for g, fns in _GRADE_FUNS.items()
}

def build_question_bank(grade):
    """Generate full 100-question bank: 30 easy, 40 medium, 30 hard."""
    bank = []
    gens_map = BANK_GENERATORS[grade]
    for diff, count in BANK_COUNTS:
        gens = gens_map[diff]
        for i in range(count):
            try:
                bank.append(gens[i % len(gens)]())
            except Exception:
                bank.append(gen_g1_addition("easy"))
    return bank

def generate_questions(grade, count):
    """Randomly select `count` questions from the 100-question bank."""
    bank = build_question_bank(grade)
    random.shuffle(bank)
    selected = bank[:min(count, len(bank))]
    for i, q in enumerate(selected):
        q["number"] = i + 1
    return selected


# ─────────────────────────────────────────────
#  VOUCHER & PROGRESS LOGIC
# ─────────────────────────────────────────────
QUARTER_MONTHS = 3          # sessions span
SESSIONS_PER_QUARTER = 12   # minimum sessions to complete a quarter
VOUCHER_AMOUNT = 300000     # VND

def get_current_quarter():
    today = date.today()
    q = (today.month - 1) // 3 + 1
    return f"{today.year}-Q{q}"

def check_and_award_voucher(student):
    """Check if student earned a new voucher for this quarter"""
    quarter = get_current_quarter()
    sessions = student.get("sessions", [])
    quarter_sessions = [s for s in sessions if s.get("quarter") == quarter]
    
    vouchers = student.setdefault("vouchers", [])
    # already has unredeemed voucher this quarter?
    existing = [v for v in vouchers if v["quarter"] == quarter and not v["redeemed"]]
    if existing:
        return None
    # already redeemed this quarter?
    redeemed = [v for v in vouchers if v["quarter"] == quarter and v["redeemed"]]
    if redeemed:
        return None
    
    if len(quarter_sessions) >= SESSIONS_PER_QUARTER:
        voucher = {
            "id": f"VCH-{quarter}-{random.randint(1000,9999)}",
            "quarter": quarter,
            "amount": VOUCHER_AMOUNT,
            "earned_date": datetime.now().strftime("%Y-%m-%d"),
            "redeemed": False,
            "redeemed_date": None
        }
        vouchers.append(voucher)
        return voucher
    return None


# ─────────────────────────────────────────────
#  API ROUTES
# ─────────────────────────────────────────────

@app.route("/api/student/login", methods=["POST"])
def student_login():
    """Login or register student by name"""
    data = request.json
    name = (data.get("name") or "").strip()
    grade = int(data.get("grade", 1))
    if not name:
        return jsonify({"error": "Name required"}), 400
    
    students = load_students()
    key = name.lower().replace(" ", "_")
    
    if key not in students:
        students[key] = {
            "id": key,
            "name": name,
            "grade": grade,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "sessions": [],
            "vouchers": [],
            "total_tests": 0,
            "total_correct": 0,
            "total_questions": 0,
        }
    else:
        # Update grade if changed
        students[key]["grade"] = grade
    
    save_students(students)
    return jsonify({"student": students[key]})


@app.route("/api/student/<student_id>", methods=["GET"])
def get_student(student_id):
    students = load_students()
    student = students.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"student": student})


@app.route("/api/questions", methods=["GET"])
def get_questions():
    grade = int(request.args.get("grade", 1))
    count = int(request.args.get("count", 10))
    count = max(5, min(100, count))  # clamp 5..100
    grade = max(1, min(5, grade))
    
    questions = generate_questions(grade, count)
    return jsonify({"questions": questions, "total": len(questions), "grade": grade})


@app.route("/api/submit", methods=["POST"])
def submit_answers():
    data = request.json
    student_id  = data.get("student_id")
    grade       = int(data.get("grade", 1))
    user_answers = data.get("answers", {})      # {qid: answer}
    skipped_ids  = data.get("skipped", [])      # list of qids skipped by timer
    question_ids = data.get("question_ids", []) # ordered list of all qids
    time_taken   = int(data.get("time_taken", 0))

    # Re-generate answers by re-running the same generators?
    # No – we must verify against the submitted question data.
    # Client sends question data + chosen answer; we re-verify server-side
    # by regenerating each question's answer from the submitted question content.
    # Since questions are generated dynamically, client must also submit
    # the correct_answers map (generated server-side and sent back encrypted/plain).
    correct_answers = data.get("correct_answers", {})  # {qid: correct_answer}
    questions_data  = data.get("questions_data", [])   # full question objects

    # Build answer map from questions_data if correct_answers not provided
    if not correct_answers and questions_data:
        for q in questions_data:
            correct_answers[str(q["id"])] = q["answer"]

    results = []
    score = 0
    skipped_count = 0
    fail_count = 0

    for qid in question_ids:
        qid_str = str(qid)
        correct = correct_answers.get(qid_str)
        user_ans = user_answers.get(qid_str)
        is_skipped = (qid_str in [str(s) for s in skipped_ids]) or (user_ans is None)
        
        # Find question data
        q_data = next((q for q in questions_data if str(q.get("id")) == qid_str), {})
        
        if is_skipped:
            status = "skip"
            skipped_count += 1
        elif user_ans == correct:
            status = "pass"
            score += 1
        else:
            status = "fail"
            fail_count += 1

        results.append({
            "id": qid,
            "level": q_data.get("level", "easy"),
            "topic": q_data.get("topic", ""),
            "question_en": q_data.get("question_en", ""),
            "question_vi": q_data.get("question_vi", ""),
            "options": q_data.get("options", []),
            "user_answer": user_ans,
            "correct_answer": correct,
            "explanation_en": q_data.get("explanation_en", ""),
            "explanation_vi": q_data.get("explanation_vi", ""),
            "status": status,  # pass / fail / skip
        })

    total = len(results)
    percentage = round((score / total) * 100) if total > 0 else 0

    if percentage >= 90:   grade_label = "Gold"
    elif percentage >= 75: grade_label = "Silver"
    elif percentage >= 60: grade_label = "Bronze"
    else:                  grade_label = "Participant"

    quarter = get_current_quarter()

    # Save to student record
    new_voucher = None
    if student_id:
        students = load_students()
        student = students.get(student_id)
        if student:
            session_entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "quarter": quarter,
                "grade": grade,
                "score": score,
                "total": total,
                "percentage": percentage,
                "grade_label": grade_label,
                "pass": score,
                "fail": fail_count,
                "skip": skipped_count,
                "time_taken": time_taken,
            }
            student.setdefault("sessions", []).append(session_entry)
            student["total_tests"]     = student.get("total_tests", 0) + 1
            student["total_correct"]   = student.get("total_correct", 0) + score
            student["total_questions"] = student.get("total_questions", 0) + total
            new_voucher = check_and_award_voucher(student)
            save_students(students)

    return jsonify({
        "score": score,
        "total": total,
        "pass": score,
        "fail": fail_count,
        "skip": skipped_count,
        "percentage": percentage,
        "grade_label": grade_label,
        "quarter": quarter,
        "new_voucher": new_voucher,
        "results": results,
        "time_taken": time_taken,
    })


@app.route("/api/student/<student_id>/vouchers", methods=["GET"])
def get_vouchers(student_id):
    students = load_students()
    student = students.get(student_id)
    if not student:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"vouchers": student.get("vouchers", [])})


@app.route("/api/student/<student_id>/redeem", methods=["POST"])
def redeem_voucher(student_id):
    """Parent redeems a voucher"""
    data = request.json
    voucher_id = data.get("voucher_id")
    pin = data.get("pin", "")
    
    # Simple parent PIN (default: "1234" – can be changed)
    PARENT_PIN = "1234"
    if pin != PARENT_PIN:
        return jsonify({"error": "Invalid PIN"}), 403
    
    students = load_students()
    student = students.get(student_id)
    if not student:
        return jsonify({"error": "Not found"}), 404
    
    for v in student.get("vouchers", []):
        if v["id"] == voucher_id and not v["redeemed"]:
            v["redeemed"] = True
            v["redeemed_date"] = datetime.now().strftime("%Y-%m-%d")
            save_students(students)
            return jsonify({"success": True, "voucher": v})
    
    return jsonify({"error": "Voucher not found or already redeemed"}), 404


@app.route("/api/student/<student_id>/progress", methods=["GET"])
def get_progress(student_id):
    """Return quarterly progress summary"""
    students = load_students()
    student = students.get(student_id)
    if not student:
        return jsonify({"error": "Not found"}), 404
    
    sessions = student.get("sessions", [])
    quarter = get_current_quarter()
    quarter_sessions = [s for s in sessions if s.get("quarter") == quarter]
    sessions_needed = SESSIONS_PER_QUARTER
    sessions_done = len(quarter_sessions)
    
    # Quarter stats
    q_scores = [s["percentage"] for s in quarter_sessions] if quarter_sessions else []
    q_avg = round(sum(q_scores) / len(q_scores), 1) if q_scores else 0
    q_best = max(q_scores) if q_scores else 0
    
    # All time trend (last 10 sessions)
    trend = [{
        "date": s["date"][:10],
        "score": s["percentage"],
        "grade_label": s.get("grade_label",""),
        "pass": s.get("pass",0),
        "fail": s.get("fail",0),
        "skip": s.get("skip",0),
    } for s in sessions[-10:]]

    # Voucher for this quarter
    vouchers = student.get("vouchers", [])
    active_voucher = next((v for v in vouchers if v["quarter"] == quarter and not v["redeemed"]), None)
    
    return jsonify({
        "student": student,
        "quarter": quarter,
        "sessions_done": sessions_done,
        "sessions_needed": sessions_needed,
        "progress_pct": min(100, round(sessions_done / sessions_needed * 100)),
        "q_avg": q_avg,
        "q_best": q_best,
        "trend": trend,
        "active_voucher": active_voucher,
        "vouchers": vouchers,
        "total_tests": student.get("total_tests", 0),
        "total_correct": student.get("total_correct", 0),
        "total_questions": student.get("total_questions", 0),
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "3.0"})


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("🦘 IKMC Math Practice Backend v3")
    print("   Dynamic question generation | Grades 1–5")
    print("   Running on http://localhost:5000")
    app.run(debug=True, port=5000)
