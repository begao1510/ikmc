# 🦘 IKMC Math Practice App — v3

Bilingual (EN/VI) math practice app for Grades 1–5, aligned with the IKMC curriculum.

## Quick Start

### Linux/macOS
```
chmod +x start.sh && ./start.sh
```

### Windows
Double-click `start-windows.bat`

### Manual
```
# Terminal 1
cd backend && pip install -r requirements.txt && python app.py

# Terminal 2
cd frontend && npm install && npm run dev
```
Open http://localhost:3000

## Key Features
- Dynamic procedurally generated questions (never the same test twice)
- Grades 1–5 with IKMC-aligned curriculum per grade
- Student login by name — progress persists in students.json
- Per-question 1-minute timer — auto-skips on timeout
- Pass / Fail / Skip summary
- Quarterly progress tracking (12 sessions = 300,000 VND voucher)
- Parent PIN voucher redemption (default PIN: 1234)
- Bilingual EN/VI toggle

## Voucher System
- Complete 12 sessions in a calendar quarter to earn a voucher
- Go to My Progress to see vouchers
- Parent enters PIN 1234 to redeem
- To change PIN: edit PARENT_PIN in backend/app.py

## Grades & Topics
- Grade 1: Addition, Subtraction, Sequences, Comparison, Word problems
- Grade 2: 2-digit arithmetic, Multiplication, Missing numbers, Geometry
- Grade 3: Division, Fractions, Perimeter, Logic
- Grade 4: Area, Factors, Averages, Speed/Distance
- Grade 5: Percentages, Ratios, Primes, Algebra, Discounts
