import json,sys
from pathlib import Path
cmd=sys.argv[1]
if cmd=="restart":
 c=json.load(open("worker.json")); ok=c["heartbeat_seconds"]==30 and c["endpoint"]=="http://localhost:9000"
 Path("runtime.json").write_text(json.dumps({"running":ok})); print("RUNNING" if ok else "FAILED");sys.exit(0 if ok else 1)
elif cmd=="status":
 r=json.load(open("runtime.json"));print("RUNNING" if r["running"] else "FAILED");sys.exit(0 if r["running"] else 1)
else:sys.exit(2)
