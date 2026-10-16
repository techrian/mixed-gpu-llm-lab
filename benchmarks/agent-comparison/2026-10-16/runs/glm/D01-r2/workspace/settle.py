import json
from decimal import Decimal

rows = {}
with open("/work/sales.csv", encoding="utf-8") as f:
    next(f)
    for line in f:
        line = line.strip()
        if not line:
            continue
        tid, dept, status, amount = line.split(",")
        if tid in rows or status == "void":
            continue
        amt = Decimal(amount)
        rows[tid] = (dept, -amt if status == "refunded" else amt)

departments = {}
total = Decimal("0")
for dept, amt in rows.values():
    departments[dept] = departments.get(dept, Decimal("0")) + amt
    total += amt

result = {
    "departments": {d: str(v.quantize(Decimal("0.01"))) for d, v in sorted(departments.items())},
    "total": str(total.quantize(Decimal("0.01"))),
    "records": len(rows),
}
with open("/work/result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
