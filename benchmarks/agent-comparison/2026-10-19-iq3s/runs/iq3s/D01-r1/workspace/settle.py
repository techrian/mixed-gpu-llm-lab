#!/usr/bin/env python3
"""Settle sales.csv -> result.json

Rules:
  - duplicate `id` rows are counted once (first occurrence wins)
  - status == 'void' rows are excluded
  - status == 'refunded' rows contribute a negative amount
  - money handled at exact 2-decimal precision (Decimal, ROUND_HALF_UP)
Output keys: departments (net per department), total, records
"""
import csv
import json
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def main():
    seen = set()
    nets = OrderedDict()
    records = 0
    dup = void = 0

    with open("sales.csv", newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = (row["id"] or "").strip()
            if not rid:
                continue
            if rid in seen:                      # duplicate id -> once only
                dup += 1
                continue
            seen.add(rid)

            status = (row["status"] or "").strip().lower()
            if status == "void":                 # excluded entirely
                void += 1
                continue

            dept = (row["department"] or "").strip()
            amt = money(row["amount"])
            if status == "refunded":
                amt = -amt                       # refunds are negative

            nets[dept] = nets.get(dept, Decimal("0.00")) + amt
            records += 1

    departments = OrderedDict(
        (d, float(nets[d].quantize(CENT, rounding=ROUND_HALF_UP)))
        for d in sorted(nets)
    )
    total = float(sum(nets.values(), Decimal("0.00")).quantize(CENT, rounding=ROUND_HALF_UP))

    result = OrderedDict(
        [("departments", departments), ("total", total), ("records", records)]
    )
    with open("result.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"skipped duplicates={dup} void={void} kept={records}")


if __name__ == "__main__":
    main()
