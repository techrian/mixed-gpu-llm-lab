import argparse,csv,json
p=argparse.ArgumentParser(description="Report existing job records. No source modification required.")
p.add_argument("--input",required=True);p.add_argument("--status",required=True);p.add_argument("--output",required=True)
a=p.parse_args();rows=list(csv.DictReader(open(a.input)));selected=[r for r in rows if r["status"]==a.status]
json.dump({"ids":sorted(r["id"] for r in selected),"count":len(selected)},open(a.output,"w"))
