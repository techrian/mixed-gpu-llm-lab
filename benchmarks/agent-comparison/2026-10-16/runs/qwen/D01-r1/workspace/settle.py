#!/usr/bin/env python3
"""Settle sales.csv into result.json.

Rules:
  * duplicate ids counted once (first occurrence wins)
  * status == 'void' excluded
  * status == 'refunded' counted as a negative amount
  * money handled with Decimal at exact 2-decimal precision (ROUND_HALF_UP)
Output object has exactly three keys: departments, total, records
"""
import csv
import json
import re
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP

SRC, DST = "sales.csv", "result.json"
CENT = Decimal("0.01")


def money(x) -> Decimal:
    return Decimal(str(x).strip()).quantize(CENT, rounding=ROUND_HALF_UP)


def tag(obj):
    """Tag Decimals as @@x.xx@@ so they can be emitted as bare JSON numbers."""
    if isinstance(obj, Decimal):
        return f"@@{obj}@@"
    if isinstance(obj, dict):
        return {k: tag(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [tag(v) for v in obj]
    return obj


def main() -> None:
    totals, seen = {}, []
    dup = void = refunds = kept = 0

    with open(SRC, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = (row["id"] or "").strip()
            if not rid:
                continue
            if rid in seen:                      # duplicate id -> skipped
                dup += 1
                continue
            seen.append(rid)

            status = (row["status"] or "").strip().lower()
            if status == "void":                 # void -> excluded
                void += 1
                continue

            amt = money(row["amount"])
            if status == "refunded":             # refunded -> negative
                amt = -amt
                refunds += 1
            else:
                pass

            dept = (row["department"] or "").strip()
            totals[dept] = totals.get(dept, Decimal("0.00")) + amt
            kept += 1

    departments = OrderedDict(sorted((k, v.quantize(CENT, rounding=ROUND_HALF_UP))
                                    for k, v in totals.items()))
    total = sum(departments.values(), Decimal("0.00")).quantize(CENT, ROUND_HALF_UP)
    payload = OrderedDict((("departments", departments),
                           ("total", total),
                           ("records", kept)))

    out = json.dumps(tag(payload), ensure_ascii=False, indent=2)
    out = re.sub(r'"@@(-?[0-9]+\.[0-9]{2})@@"', r"\1", out)
    with open(DST, "w", encoding="utf-8") as fh:
        fh.write(out + "\n")

    print(f"ids_seen={len(seen)} dup_ignored={dup} void_excluded={void} "
          f"refunds={refunds} records={payload['records']}")


if __name__ == "__main__":
    main()
