import json
x=json.load(open("services.json")); assert 10 <= x["services"]["api"]["timeout_seconds"] <= 90; print("VALID")
