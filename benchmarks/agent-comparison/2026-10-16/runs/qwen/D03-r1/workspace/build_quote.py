#!/usr/bin/env python3
"""Generate quote.json with 100 quote entries.

Basis (read from source files in /work/docs):
  - docs/prices-2026.txt: "Approved current price list, effective 2026-10-01.
    Widget unit price 15 USD. Supersedes all earlier price lists."
  - docs/discount-policy.txt: "Current approved discount: quantities >=100 receive
    10 percent off the unit-price subtotal; no other fees."
  - docs/prices-2025.txt is explicitly superseded and is NOT used.
"""
import json
from decimal import Decimal, ROUND_HALF_UP

PRICE_FILE = "docs/prices-2026.txt"
DISCOUNT_FILE = "docs/discount-policy.txt"

UNIT_PRICE = Decimal("15.00")   # from prices-2026.txt (current, effective 2026-10-01)
CURRENCY = "USD"
DISCOUNT_PCT = Decimal("10")    # from discount-policy.txt, applies at qty >= 100
DISCOUNT_THRESHOLD = 100

entries = []
for qty in range(1, 101):
    pct = DISCOUNT_PCT if qty >= DISCOUNT_THRESHOLD else Decimal("0")
    subtotal = (UNIT_PRICE * Decimal(qty)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    discount_amt = (subtotal * pct / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (subtotal - discount_amt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    entries.append({
        "unit_price": float(UNIT_PRICE),
        "quantity": qty,
        "discount_pct": float(pct),
        "total": float(total),
        "currency": CURRENCY,
        "sources": [PRICE_FILE, DISCOUNT_FILE],
    })

with open("quote.json", "w", encoding="utf-8") as fh:
    json.dump(entries, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("entries:", len(entries))
print("discounted entries:", sum(1 for e in entries if e["discount_pct"]))
print("first:", entries[0])
print("last:", entries[-1])
