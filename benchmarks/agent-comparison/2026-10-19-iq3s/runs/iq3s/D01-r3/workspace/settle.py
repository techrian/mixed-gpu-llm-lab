#!/usr/bin/env python3
"""Settle sales.csv -> result.json.

Rules:
  - duplicate ids counted once (first occurrence kept)
  - status 'void' excluded entirely
  - status 'refunded' contributes as a negative amount
  - money handled with Decimal, quantized to 0.01 (ROUND_HALF_UP)
Output object has exactly three keys: departments, total, records.
"""
import csv
import json
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value).strip() or "0").quantize(CENT, rounding=ROUND_HALF_UP)


def main():
    seen = set()
    net = OrderedDict()
    records = 0

    with open("sales.csv", newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            rid = (row.get("id") or "").strip()
            if not rid or rid in seen:
                continue          # duplicate id -> counted once
            seen.add(rid)

            status = (row.get("status") or "").strip().lower()
            if status == "void":
                continue          # excluded from totals and record count

            dept = (row.get("department") or "").strip() or "unknown"
            amount = money(row.get("amount"))
            if status == "refunded":
                amount = -abs(amount)

            net[dept] = net.get(dept, Decimal("0.00")) + amount
            records += 1

    departments = OrderedDict(
        (d, float(v.quantize(CENT, rounding=ROUND_HALF_UP)))
        for d, v in sorted(net.items())
    )
    total = sum(net.values(), Decimal("0.00")).quantize(CENT, rounding=ROUND_HALF_UP)

    result = OrderedDict(
        [("departments", departments), ("total", float(total)), ("records", records)]
    )
    with open("result.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
