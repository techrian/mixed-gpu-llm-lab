import json
import os
import sys
import time
import urllib.request
from pathlib import Path

label = sys.argv[1]
prefill = int(sys.argv[2])
reserve_mib = int(sys.argv[3])
base = os.environ.get("STRATA_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
# About 62k tokens of deterministic context; identical for each arm except its
# four-character leading run label, which prevents a cached prompt prefix.
paragraph = (
    "Record 1842: The archive lists a cedar cabinet, a brass compass, a blue notebook, "
    "and a small glass bottle. The clerk checked each item, copied its condition, and "
    "placed the record in the west wing ledger. No item was moved during the inspection. "
)
context = f"Benchmark {label}.\n" + paragraph * 1100
body = {
    "model": "orcarouter-qwen3.8-flash-next-uncensored-q4_k_m",
    "messages": [{"role": "user", "content": context +
        "\nContinue with at least 512 concise numbered observations. Do not summarize or stop early."}],
    "max_tokens": 512,
    "temperature": 0.7,
    "stream": False,
}
req = urllib.request.Request(base + "/v1/chat/completions", data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=900) as r:
    response = json.load(r)
elapsed = time.time() - t0
with urllib.request.urlopen(base + "/metrics", timeout=20) as r:
    metrics = json.load(r)
last = metrics["requests"][0]
result = {
    "label": label,
    "config_prefill": prefill,
    "config_reserve_mib": reserve_mib,
    "wall_s": round(elapsed, 3),
    "response_usage": response.get("usage"),
    "response_finish": response.get("choices", [{}])[0].get("finish_reason"),
    "metrics": last,
    "engine": {k: metrics.get("engine", {}).get(k) for k in
               ("max_context", "kv", "expert_slots", "expert_cache_mib", "vram_free_mib")},
    "gpu": metrics.get("hardware", {}).get("gpus"),
}
output_dir = Path(os.environ.get("STRATA_BENCH_OUTPUT_DIR", str(Path(__file__).resolve().parents[2] / "new-runs" / Path(__file__).parent.name)))
output_dir.mkdir(parents=True, exist_ok=True)
out = output_dir / f"{label}.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
