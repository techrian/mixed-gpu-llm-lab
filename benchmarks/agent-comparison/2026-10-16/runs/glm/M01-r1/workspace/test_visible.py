from timeutil import as_utc
from datetime import timezone
assert as_utc("2026-10-16T09:00:00+09:00").hour == 0
assert as_utc("2026-10-16T00:00:00Z").tzinfo == timezone.utc
print("visible tests PASS")
