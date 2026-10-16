#!/usr/bin/env python3
"""Settle sales.csv -> result.json.

Rules applied:
- duplicate ids counted once (first occurrence wins)
- status 'void' rows excluded entirely
- status 'refunded' rows contribute a negative amount
- money computed with Decimal, rounded to exactly 2 decimal places (HALF_UP)
- output holds exactly three keys: departments, total, records
"""
import csv
import json
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

SRC = "sales.csv"
DST = "result.json"


def money(value: Decimal) -> float:
    """Round to the second decimal place (half-up) and return a plain number."""
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def main() -> None:
    seen = set()
    net = {}
    records = 0

    with open(SRC, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row = {
                k.strip(): (v or "").strip()
                for k, v in row.items()
                if k is not None
            }
            rid = row.get("id", "")
            if not rid or rid in seen:      # id 중복 -> 첫 건만 반영
                continue
            seen.add(rid)

            status = row.get("status", "").lower()
            if status == "void":             # void는 제외
                continue

            amount = Decimal(row["amount"])
            if status == "refunded":         # refunded는 음수
                amount = -amount

            dept = row["department"]
            net[dept] = net.get(dept, Decimal("0.00")) + amount
            records += 1

    departments = OrderedDict((d, money(v)) for d, v in sorted(net.items()))
    total = sum(net.values(), Decimal("0.00"))

    out = OrderedDict(
        [
            ("departments", departments),
            ("total", money(total)),
            ("records", records),
        ]
    )
    with open(DST, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
