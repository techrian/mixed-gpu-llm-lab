#!/usr/bin/env python3
"""Reconcile sales.csv -> result.json

Rules:
  * duplicate ids are counted once (first occurrence wins)
  * status 'void' rows are excluded entirely
  * status 'refunded' rows contribute a negative amount
  * all other statuses contribute a positive amount
  * money handled with Decimal, quantized to 0.01 (ROUND_HALF_UP)
Output keys: departments (net per department), total, records
"""
import csv
import json
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
SRC = "sales.csv"
DST = "result.json"


def money(value):
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def main():
    seen = set()
    net = {}
    records = 0

    with open(SRC, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = (row.get("id") or "").strip()
            dept = (row.get("department") or "").strip()
            status = (row.get("status") or "").strip().lower()
            raw = (row.get("amount") or "").strip()

            if not rid or not raw:
                continue
            if rid in seen:            # duplicate id -> counted once
                continue
            seen.add(rid)
            if status == "void":       # void -> excluded
                continue

            amount = money(raw)
            amount = -abs(amount) if status == "refunded" else abs(amount)

            net[dept] = net.get(dept, Decimal("0.00")) + amount
            records += 1

    net = OrderedDict((d, money(v)) for d, v in sorted(net.items()))
    total = money(sum(net.values(), Decimal("0.00")))

    # Emit numbers with exact 2-decimal precision (JSON numbers, not strings).
    lines = ["{", '  "departments": {']
    items = [f'    {json.dumps(d)}: {v:.2f}' for d, v in net.items()]
    lines.append(",\n".join(items))
    lines += ["  },", f'  "total": {total:.2f},', f'  "records": {records}', "}"]
    text = "\n".join(lines) + "\n"

    with open(DST, "w", encoding="utf-8") as fh:
        fh.write(text)

    print(text, end="")


if __name__ == "__main__":
    main()
