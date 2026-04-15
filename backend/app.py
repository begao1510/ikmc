"""
IKMC Math Practice – Backend v3
Dynamic question generation per grade (1-5), student profiles,
3-month progress tracking, voucher system.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import random, json, os, math
from datetime import datetime, date

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


# ── GRADE 1 ──────────────────────────────────
def gen_g1_addition():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    ans = a + b
    wrong = _wrongs_near(ans, 1, 20)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(1),
        "question_en": f"What is {a} + {b}?",
        "question_vi": f"{a} + {b} bằng bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{a} + {b} = {ans}.",
        "explanation_vi": f"{a} + {b} = {ans}.",
        "topic": "addition"
    }

def gen_g1_subtraction():
    b = random.randint(1, 9)
    a = random.randint(b, 10)
    ans = a - b
    wrong = _wrongs_near(ans, 0, 10)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(1),
        "question_en": f"What is {a} − {b}?",
        "question_vi": f"{a} − {b} bằng bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{a} − {b} = {ans}.",
        "explanation_vi": f"{a} − {b} = {ans}.",
        "topic": "subtraction"
    }

def gen_g1_sequence():
    step = random.choice([1, 2])
    start = random.randint(1, 8)
    seq = [start + i * step for i in range(6)]
    pos = random.randint(1, 4)
    ans = seq[pos]
    display = [str(x) if i != pos else "__" for i, x in enumerate(seq)]
    wrong = _wrongs_near(ans, 1, 20)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(1),
        "question_en": f"Find the missing number: {', '.join(display)}",
        "question_vi": f"Tìm số còn thiếu: {', '.join(display)}",
        "options": opts, "answer": str(ans),
        "explanation_en": f"The pattern goes +{step} each time. Answer: {ans}.",
        "explanation_vi": f"Quy luật cộng {step} mỗi bước. Đáp án: {ans}.",
        "topic": "patterns"
    }

def gen_g1_comparison():
    a, b = random.sample(range(1, 20), 2)
    bigger = max(a, b)
    wrong = _wrongs_near(bigger, 1, 20)
    opts = _shuffle_opts(str(bigger), wrong)
    return {
        "id": make_id(), "level": _level(1),
        "question_en": f"Which is larger: {a} or {b}?",
        "question_vi": f"Số nào lớn hơn: {a} hay {b}?",
        "options": opts, "answer": str(bigger),
        "explanation_en": f"{bigger} is larger than {min(a,b)}.",
        "explanation_vi": f"{bigger} lớn hơn {min(a,b)}.",
        "topic": "comparison"
    }

def gen_g1_word_problem():
    a = random.randint(2, 8)
    b = random.randint(1, 5)
    op = random.choice(["+", "-"])
    if op == "+":
        ans = a + b
        en = f"There are {a} apples in a basket. {b} more are added. How many apples now?"
        vi = f"Có {a} quả táo trong rổ. Thêm {b} quả nữa. Bây giờ có bao nhiêu quả?"
        exp_en = f"{a} + {b} = {ans} apples."
        exp_vi = f"{a} + {b} = {ans} quả táo."
    else:
        ans = a - b
        en = f"There are {a} birds on a fence. {b} fly away. How many remain?"
        vi = f"Có {a} con chim trên hàng rào. {b} con bay đi. Còn lại bao nhiêu?"
        exp_en = f"{a} − {b} = {ans} birds."
        exp_vi = f"{a} − {b} = {ans} con chim."
    wrong = _wrongs_near(ans, 0, 15)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(1),
        "question_en": en, "question_vi": vi,
        "options": opts, "answer": str(ans),
        "explanation_en": exp_en, "explanation_vi": exp_vi,
        "topic": "word_problems"
    }


# ── GRADE 2 ──────────────────────────────────
def gen_g2_addition():
    a = random.randint(10, 50)
    b = random.randint(10, 50)
    ans = a + b
    wrong = _wrongs_near(ans, 10, 100)
    return _make_q(2, f"{a} + {b}", ans, wrong, "addition")

def gen_g2_multiplication():
    a = random.randint(2, 5)
    b = random.randint(2, 9)
    ans = a * b
    wrong = _wrongs_near(ans, 4, 50)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(2),
        "question_en": f"What is {a} × {b}?",
        "question_vi": f"{a} × {b} bằng bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{a} × {b} = {ans}. ({a} groups of {b})",
        "explanation_vi": f"{a} × {b} = {ans}. ({a} nhóm, mỗi nhóm {b})",
        "topic": "multiplication"
    }

def gen_g2_missing_number():
    a = random.randint(5, 30)
    b = random.randint(1, 20)
    ans = a + b
    side = random.choice(["left", "right"])
    if side == "left":
        en = f"■ + {b} = {ans}. What is ■?"
        vi = f"■ + {b} = {ans}. ■ bằng bao nhiêu?"
        res = a
    else:
        en = f"{a} + ■ = {ans}. What is ■?"
        vi = f"{a} + ■ = {ans}. ■ bằng bao nhiêu?"
        res = b
    wrong = _wrongs_near(res, 1, 30)
    opts = _shuffle_opts(str(res), wrong)
    return {
        "id": make_id(), "level": _level(2),
        "question_en": en, "question_vi": vi,
        "options": opts, "answer": str(res),
        "explanation_en": f"■ = {ans} − {b if side=='left' else a} = {res}.",
        "explanation_vi": f"■ = {ans} − {b if side=='left' else a} = {res}.",
        "topic": "missing_number"
    }

def gen_g2_geometry():
    shapes = [
        {"name_en":"triangle","name_vi":"tam giác","sides":3},
        {"name_en":"square","name_vi":"hình vuông","sides":4},
        {"name_en":"pentagon","name_vi":"ngũ giác","sides":5},
        {"name_en":"hexagon","name_vi":"lục giác","sides":6},
    ]
    sh = random.choice(shapes)
    count = random.randint(2, 4)
    ans = sh["sides"] * count
    wrong = _wrongs_near(ans, 2, 30)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(2),
        "question_en": f"How many sides do {count} {sh['name_en']}s have in total?",
        "question_vi": f"{count} {sh['name_vi']} có tổng cộng bao nhiêu cạnh?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"Each {sh['name_en']} has {sh['sides']} sides. {count} × {sh['sides']} = {ans}.",
        "explanation_vi": f"Mỗi {sh['name_vi']} có {sh['sides']} cạnh. {count} × {sh['sides']} = {ans}.",
        "topic": "geometry"
    }

def gen_g2_word_problem():
    items = random.choice(["pencils","books","candies","marbles","stickers"])
    items_vi = {"pencils":"bút chì","books":"quyển sách","candies":"kẹo","marbles":"viên bi","stickers":"nhãn dán"}[items]
    bags = random.randint(2, 5)
    each = random.randint(3, 8)
    give = random.randint(1, bags * each - 2)
    total = bags * each
    ans = total - give
    wrong = _wrongs_near(ans, 1, 40)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(2),
        "question_en": f"Sam has {bags} bags with {each} {items} each. He gives away {give}. How many does he have left?",
        "question_vi": f"Sam có {bags} túi, mỗi túi {each} {items_vi}. Anh ấy cho đi {give}. Còn lại bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{bags} × {each} = {total}. {total} − {give} = {ans} {items}.",
        "explanation_vi": f"{bags} × {each} = {total}. {total} − {give} = {ans} {items_vi}.",
        "topic": "word_problems"
    }


# ── GRADE 3 ──────────────────────────────────
def gen_g3_multiplication():
    a = random.randint(6, 12)
    b = random.randint(6, 12)
    ans = a * b
    wrong = _wrongs_near(ans, 20, 150)
    return _make_q(3, f"{a} × {b}", ans, wrong, "multiplication")

def gen_g3_division():
    b = random.randint(2, 9)
    ans = random.randint(2, 12)
    a = b * ans
    wrong = _wrongs_near(ans, 1, 20)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(3),
        "question_en": f"What is {a} ÷ {b}?",
        "question_vi": f"{a} ÷ {b} bằng bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{a} ÷ {b} = {ans}.",
        "explanation_vi": f"{a} ÷ {b} = {ans}.",
        "topic": "division"
    }

def gen_g3_fractions():
    denom = random.choice([2, 4, 5, 10])
    numer = random.randint(1, denom - 1)
    total = random.randint(denom * 2, denom * 6)
    if total % denom != 0:
        total = total - total % denom
    ans = (total * numer) // denom
    wrong = _wrongs_near(ans, 1, total)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(3),
        "question_en": f"What is {numer}/{denom} of {total}?",
        "question_vi": f"{numer}/{denom} của {total} bằng bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{total} ÷ {denom} × {numer} = {total//denom} × {numer} = {ans}.",
        "explanation_vi": f"{total} ÷ {denom} × {numer} = {total//denom} × {numer} = {ans}.",
        "topic": "fractions"
    }

def gen_g3_perimeter():
    shape = random.choice(["square","rectangle","triangle"])
    if shape == "square":
        s = random.randint(3, 12)
        ans = 4 * s
        en = f"A square has side {s} cm. What is its perimeter?"
        vi = f"Hình vuông cạnh {s} cm. Chu vi là bao nhiêu?"
        exp_en = f"Perimeter = 4 × {s} = {ans} cm."
        exp_vi = f"Chu vi = 4 × {s} = {ans} cm."
    elif shape == "rectangle":
        l = random.randint(4, 12); w = random.randint(2, l-1)
        ans = 2 * (l + w)
        en = f"A rectangle is {l} cm long and {w} cm wide. What is its perimeter?"
        vi = f"Hình chữ nhật dài {l} cm, rộng {w} cm. Chu vi là bao nhiêu?"
        exp_en = f"Perimeter = 2 × ({l} + {w}) = 2 × {l+w} = {ans} cm."
        exp_vi = f"Chu vi = 2 × ({l} + {w}) = {ans} cm."
    else:
        a, b, c = random.randint(3,8), random.randint(3,8), random.randint(3,8)
        ans = a + b + c
        en = f"A triangle has sides {a} cm, {b} cm, and {c} cm. What is its perimeter?"
        vi = f"Tam giác có 3 cạnh {a} cm, {b} cm và {c} cm. Chu vi là bao nhiêu?"
        exp_en = f"Perimeter = {a} + {b} + {c} = {ans} cm."
        exp_vi = f"Chu vi = {a} + {b} + {c} = {ans} cm."
    wrong = _wrongs_near(ans, 5, 80)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(3),
        "question_en": en, "question_vi": vi,
        "options": opts, "answer": str(ans),
        "explanation_en": exp_en, "explanation_vi": exp_vi,
        "topic": "geometry"
    }

def gen_g3_logic():
    a = random.randint(5, 15)
    extra = random.randint(2, 8)
    b = a + extra
    total = a + b
    en = f"Two numbers sum to {total}. One number is {extra} more than the other. What is the smaller number?"
    vi = f"Hai số có tổng là {total}. Số này hơn số kia {extra}. Số nhỏ hơn là bao nhiêu?"
    wrong = _wrongs_near(a, 1, total)
    opts = _shuffle_opts(str(a), wrong)
    return {
        "id": make_id(), "level": _level(3),
        "question_en": en, "question_vi": vi,
        "options": opts, "answer": str(a),
        "explanation_en": f"Let smaller = x. Then x + (x+{extra}) = {total} → 2x = {total-extra} → x = {a}.",
        "explanation_vi": f"Gọi số nhỏ = x. x + (x+{extra}) = {total} → 2x = {total-extra} → x = {a}.",
        "topic": "logic"
    }

def gen_g3_word_problem():
    price = random.randint(3, 9)
    qty = random.randint(3, 8)
    paid = price * qty + random.randint(1, 5) * price
    total_cost = price * qty
    change = paid - total_cost
    en = f"Each notebook costs {price} coins. Tom buys {qty} notebooks and pays {paid} coins. How much change does he get?"
    vi = f"Mỗi quyển sách giá {price} xu. Tom mua {qty} quyển và trả {paid} xu. Tom được trả lại bao nhiêu?"
    wrong = _wrongs_near(change, 1, 30)
    opts = _shuffle_opts(str(change), wrong)
    return {
        "id": make_id(), "level": _level(3),
        "question_en": en, "question_vi": vi,
        "options": opts, "answer": str(change),
        "explanation_en": f"Total cost: {price} × {qty} = {total_cost}. Change: {paid} − {total_cost} = {change}.",
        "explanation_vi": f"Tổng tiền: {price} × {qty} = {total_cost}. Tiền thừa: {paid} − {total_cost} = {change}.",
        "topic": "word_problems"
    }


# ── GRADE 4 ──────────────────────────────────
def gen_g4_large_arithmetic():
    ops = [("×", lambda a,b: a*b), ("+", lambda a,b: a+b), ("−", lambda a,b: a-b)]
    sym, fn = random.choice(ops)
    if sym == "×":
        a = random.randint(12, 25); b = random.randint(12, 25)
    elif sym == "+":
        a = random.randint(100, 500); b = random.randint(100, 500)
    else:
        a = random.randint(200, 999); b = random.randint(100, a-50)
    ans = fn(a, b)
    wrong = _wrongs_near(ans, 10, ans + 100)
    return _make_q(4, f"{a} {sym} {b}", ans, wrong, "arithmetic")

def gen_g4_area():
    shape = random.choice(["square", "rectangle"])
    if shape == "square":
        s = random.randint(4, 15)
        ans = s * s
        en = f"A square has side {s} cm. What is its area?"
        vi = f"Hình vuông cạnh {s} cm. Diện tích là bao nhiêu?"
        exp_en = f"Area = {s} × {s} = {ans} cm²."
        exp_vi = f"Diện tích = {s} × {s} = {ans} cm²."
    else:
        l = random.randint(5, 15); w = random.randint(3, l)
        ans = l * w
        en = f"A rectangle is {l} cm by {w} cm. What is its area?"
        vi = f"Hình chữ nhật {l} cm × {w} cm. Diện tích là bao nhiêu?"
        exp_en = f"Area = {l} × {w} = {ans} cm²."
        exp_vi = f"Diện tích = {l} × {w} = {ans} cm²."
    wrong = _wrongs_near(ans, 5, ans + 50)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(4),
        "question_en": en, "question_vi": vi, "options": opts, "answer": str(ans),
        "explanation_en": exp_en, "explanation_vi": exp_vi, "topic": "geometry"
    }

def gen_g4_factors():
    n = random.choice([12, 16, 18, 20, 24, 30, 36])
    factors = [i for i in range(1, n+1) if n % i == 0]
    ans = len(factors)
    wrong = _wrongs_near(ans, 1, 12)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(4),
        "question_en": f"How many factors does {n} have?",
        "question_vi": f"Số {n} có bao nhiêu ước số?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"Factors of {n}: {factors}. Total: {ans}.",
        "explanation_vi": f"Ước của {n}: {factors}. Tổng: {ans}.",
        "topic": "number_theory"
    }

def gen_g4_average():
    count = random.randint(3, 5)
    nums = [random.randint(10, 30) for _ in range(count)]
    total = sum(nums)
    ans = total // count
    wrong = _wrongs_near(ans, 5, 40)
    opts = _shuffle_opts(str(ans), wrong)
    nums_str = ", ".join(map(str, nums))
    return {
        "id": make_id(), "level": _level(4),
        "question_en": f"What is the average of: {nums_str}?",
        "question_vi": f"Trung bình cộng của: {nums_str} là bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"Sum = {total}. Average = {total} ÷ {count} = {ans}.",
        "explanation_vi": f"Tổng = {total}. Trung bình = {total} ÷ {count} = {ans}.",
        "topic": "statistics"
    }

def gen_g4_logic():
    # Working backwards
    result = random.randint(5, 15)
    add_last = random.randint(2, 8)
    mul_first = random.randint(2, 5)
    original = (result - add_last) // mul_first if (result - add_last) % mul_first == 0 else None
    if original is None or original < 1:
        original = random.randint(2, 6)
        mul_first = 2
        add_last = random.randint(1, 5)
        result = original * mul_first + add_last
    wrong = _wrongs_near(original, 1, 20)
    opts = _shuffle_opts(str(original), wrong)
    return {
        "id": make_id(), "level": _level(4),
        "question_en": f"A number is multiplied by {mul_first}, then {add_last} is added. The result is {result}. What was the original number?",
        "question_vi": f"Một số nhân với {mul_first}, rồi cộng thêm {add_last}. Kết quả là {result}. Số ban đầu là bao nhiêu?",
        "options": opts, "answer": str(original),
        "explanation_en": f"Work backwards: ({result} − {add_last}) ÷ {mul_first} = {result-add_last} ÷ {mul_first} = {original}.",
        "explanation_vi": f"Làm ngược lại: ({result} − {add_last}) ÷ {mul_first} = {original}.",
        "topic": "logic"
    }

def gen_g4_word_problem():
    speed = random.randint(4, 8)
    hours = random.randint(3, 6)
    dist = speed * hours
    en = f"A cyclist travels at {speed} km/h. How far does she travel in {hours} hours?"
    vi = f"Một người đạp xe với tốc độ {speed} km/h. Sau {hours} giờ, người đó đi được bao nhiêu km?"
    wrong = _wrongs_near(dist, 5, 60)
    opts = _shuffle_opts(str(dist), wrong)
    return {
        "id": make_id(), "level": _level(4),
        "question_en": en, "question_vi": vi, "options": opts, "answer": str(dist),
        "explanation_en": f"Distance = {speed} × {hours} = {dist} km.",
        "explanation_vi": f"Quãng đường = {speed} × {hours} = {dist} km.",
        "topic": "word_problems"
    }


# ── GRADE 5 ──────────────────────────────────
def gen_g5_percentage():
    pct = random.choice([10, 20, 25, 50, 75])
    total = random.choice([40, 60, 80, 100, 120, 200])
    ans = (total * pct) // 100
    wrong = _wrongs_near(ans, 5, total)
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(5),
        "question_en": f"What is {pct}% of {total}?",
        "question_vi": f"{pct}% của {total} là bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{pct}% of {total} = {total} × {pct}/100 = {ans}.",
        "explanation_vi": f"{pct}% của {total} = {total} × {pct}/100 = {ans}.",
        "topic": "percentages"
    }

def gen_g5_ratio():
    a = random.randint(2, 6); b = random.randint(2, 6)
    total = random.randint(3, 8) * (a + b)
    part_a = (total * a) // (a + b)
    wrong = _wrongs_near(part_a, 5, total)
    opts = _shuffle_opts(str(part_a), wrong)
    return {
        "id": make_id(), "level": _level(5),
        "question_en": f"Two numbers are in the ratio {a}:{b}. Their sum is {total}. What is the larger part?",
        "question_vi": f"Hai số có tỉ lệ {a}:{b}. Tổng của chúng là {total}. Phần lớn hơn là bao nhiêu?",
        "options": opts, "answer": str(max(part_a, total - part_a)),
        "explanation_en": f"Each part = {total}÷{a+b}={total//(a+b)}. Larger = {max(a,b)} × {total//(a+b)} = {max(part_a,total-part_a)}.",
        "explanation_vi": f"Mỗi phần = {total}÷{a+b}={total//(a+b)}. Phần lớn = {max(a,b)} × {total//(a+b)} = {max(part_a,total-part_a)}.",
        "topic": "ratios"
    }

def gen_g5_prime():
    primes_to_50 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]
    non_primes = [4,6,8,9,10,12,14,15,16,18,20,21,22,25,26,27,28]
    target = random.choice(primes_to_50)
    wrong_choices = random.sample([x for x in non_primes if x != target], 3)
    opts = _shuffle_opts(str(target), [str(x) for x in wrong_choices])
    return {
        "id": make_id(), "level": _level(5),
        "question_en": f"Which of these numbers is prime?",
        "question_vi": f"Số nào trong các số sau là số nguyên tố?",
        "options": opts, "answer": str(target),
        "explanation_en": f"{target} is prime because it has only 2 factors: 1 and itself.",
        "explanation_vi": f"{target} là số nguyên tố vì chỉ có 2 ước là 1 và chính nó.",
        "topic": "number_theory"
    }

def gen_g5_speed_time():
    dist = random.choice([60, 80, 90, 120, 150, 200])
    speed = random.choice([30, 40, 50, 60])
    time = dist // speed
    wrong = _wrongs_near(time, 1, 10)
    opts = _shuffle_opts(str(time), wrong)
    return {
        "id": make_id(), "level": _level(5),
        "question_en": f"A car travels {dist} km at {speed} km/h. How many hours does it take?",
        "question_vi": f"Ô tô đi {dist} km với tốc độ {speed} km/h. Mất bao nhiêu giờ?",
        "options": opts, "answer": str(time),
        "explanation_en": f"Time = {dist} ÷ {speed} = {time} hours.",
        "explanation_vi": f"Thời gian = {dist} ÷ {speed} = {time} giờ.",
        "topic": "speed_time"
    }

def gen_g5_algebra():
    x = random.randint(3, 12)
    m = random.randint(2, 5)
    c = random.randint(1, 10)
    result = m * x + c
    wrong = _wrongs_near(x, 1, 20)
    opts = _shuffle_opts(str(x), wrong)
    return {
        "id": make_id(), "level": _level(5),
        "question_en": f"Solve: {m}x + {c} = {result}. What is x?",
        "question_vi": f"Giải: {m}x + {c} = {result}. x bằng bao nhiêu?",
        "options": opts, "answer": str(x),
        "explanation_en": f"{m}x = {result} − {c} = {result-c}. x = {result-c} ÷ {m} = {x}.",
        "explanation_vi": f"{m}x = {result} − {c} = {result-c}. x = {result-c} ÷ {m} = {x}.",
        "topic": "algebra"
    }

def gen_g5_word_problem():
    unit_price = random.randint(5, 20)
    qty = random.randint(5, 15)
    discount_pct = random.choice([10, 20, 25])
    original = unit_price * qty
    discount = (original * discount_pct) // 100
    final = original - discount
    wrong = _wrongs_near(final, 10, original)
    opts = _shuffle_opts(str(final), wrong)
    return {
        "id": make_id(), "level": _level(5),
        "question_en": f"A shirt costs {unit_price} coins. Buy {qty} and get {discount_pct}% off the total. How much do you pay?",
        "question_vi": f"Áo giá {unit_price} xu. Mua {qty} chiếc được giảm {discount_pct}% tổng tiền. Phải trả bao nhiêu?",
        "options": opts, "answer": str(final),
        "explanation_en": f"Total: {unit_price}×{qty}={original}. Discount: {discount}. Pay: {original}−{discount}={final}.",
        "explanation_vi": f"Tổng: {unit_price}×{qty}={original}. Giảm: {discount}. Trả: {original}−{discount}={final}.",
        "topic": "word_problems"
    }


# ── HELPERS ──────────────────────────────────
def _level(grade):
    """Map grade to difficulty label for IKMC"""
    return {1:"easy",2:"easy",3:"medium",4:"medium",5:"hard"}[grade]

def _wrongs_near(ans, lo, hi):
    """Generate 3 plausible wrong answers"""
    ans_int = int(ans) if isinstance(ans, (int, float)) else ans
    wrongs = set()
    attempts = 0
    while len(wrongs) < 3 and attempts < 200:
        attempts += 1
        delta = random.choice([-3,-2,-1,1,2,3,4,5,-4,-5])
        cand = ans_int + delta
        if lo <= cand <= hi and cand != ans_int:
            wrongs.add(str(cand))
    # fallback
    while len(wrongs) < 3:
        cand = random.randint(max(lo, ans_int-10), min(hi, ans_int+10))
        if str(cand) != str(ans_int):
            wrongs.add(str(cand))
    return list(wrongs)

def _shuffle_opts(correct, wrongs):
    pool = [correct] + wrongs[:3]
    random.shuffle(pool)
    return pool[:4]

def _make_q(grade, expr, ans, wrong, topic):
    opts = _shuffle_opts(str(ans), wrong)
    return {
        "id": make_id(), "level": _level(grade),
        "question_en": f"What is {expr}?",
        "question_vi": f"{expr} bằng bao nhiêu?",
        "options": opts, "answer": str(ans),
        "explanation_en": f"{expr} = {ans}.",
        "explanation_vi": f"{expr} = {ans}.",
        "topic": topic
    }


# ── GRADE GENERATORS MAP ─────────────────────
GRADE_GENERATORS = {
    1: [gen_g1_addition, gen_g1_subtraction, gen_g1_sequence,
        gen_g1_comparison, gen_g1_word_problem],
    2: [gen_g2_addition, gen_g2_multiplication, gen_g2_missing_number,
        gen_g2_geometry, gen_g2_word_problem],
    3: [gen_g3_multiplication, gen_g3_division, gen_g3_fractions,
        gen_g3_perimeter, gen_g3_logic, gen_g3_word_problem],
    4: [gen_g4_large_arithmetic, gen_g4_area, gen_g4_factors,
        gen_g4_average, gen_g4_logic, gen_g4_word_problem],
    5: [gen_g5_percentage, gen_g5_ratio, gen_g5_prime,
        gen_g5_speed_time, gen_g5_algebra, gen_g5_word_problem],
}

def generate_questions(grade, count):
    """Generate `count` questions for the given grade, balanced across topics"""
    gens = GRADE_GENERATORS.get(grade, GRADE_GENERATORS[1])
    questions = []
    used_topics = []
    for i in range(count):
        # rotate through generators to ensure variety
        gen = gens[i % len(gens)]
        try:
            q = gen()
            q["number"] = i + 1
            questions.append(q)
        except Exception as e:
            # fallback to addition if generator fails
            q = gen_g1_addition()
            q["number"] = i + 1
            questions.append(q)
    random.shuffle(questions)
    for i, q in enumerate(questions):
        q["number"] = i + 1
    return questions


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
    count = max(5, min(30, count))  # clamp 5..30
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
