import json,shutil
from pathlib import Path
from suite import build_tasks,World,verify
ROOT=Path(__file__).resolve().parent

def oracle(w):
 t=w.task.id
 def call(n,**a):return w.call(n,a)
 def read(p):return call('read_file',path=p)
 def put(p,v):call('write_file',path=p,content=json.dumps(v,ensure_ascii=False));read(p)
 def get(c,id):return call('record_get',collection=c,id=id)
 def ls(c,**a):return call('records_list',collection=c,**a)
 def upd(c,id,changes):r=get(c,id);call('record_update',collection=c,id=id,changes=changes,expected_version=r['version']);get(c,id)
 def create(c,r,key):call('record_create',collection=c,record=r,idempotency_key=key);ls(c)
 def term(s):return call('terminal',command=s)
 final='Completed and verified.'
 if t=='T01':call('create_reminder',title='Submit weekly expense report',when='2026-10-17T18:00:00',timezone='Asia/Seoul',repeat='none');ls('reminders')
 elif t=='T02':
  for s in ('api','billing','worker'):call('service_status',service_id=s)
  final=json.dumps({'unhealthy':['billing'],'healthy_count':2})
 elif t=='T03':read('policy.txt');ls('contacts');ls('tickets');upd('tickets','TK91',{'owner':'fin-oncall'})
 elif t=='T04':final='135 minutes'
 elif t=='W01':read('policy.txt');get('orders','O-304');create('refunds',{'order_id':'O-304','sku':'mouse','quantity':1,'amount':24.95,'currency':'USD'},'refund-O304-mouse-1')
 elif t=='W02':ls('events');upd('events','E-22',{'starts_at':'2026-11-02T18:00:00Z','ends_at':'2026-11-02T18:30:00Z'})
 elif t=='W03':
  found=call('search_files',query='supplier',path='/work')['matches'];assert found
  read(found[0]['path']);ls('inventory');create('purchases',{'sku':'S-17','supplier_id':'SUP-A','quantity':20,'unit_price':7,'total':140,'currency':'USD'},'restock-S17-20261016')
 elif t=='W04':
  cursor=None
  while True:
   a=ls('jobs',**({'cursor':cursor} if cursor else {}));cursor=a['next_cursor']
   if cursor is None:break
  ls('followups');create('followups',{'source_id':'J11','owner':'ops','title':'Follow up J11'},'job-J11')
 elif t=='D01':read('sales.csv');put('result.json',{'departments':{'ops':25.0,'support':40.1},'total':65.1,'records':5})
 elif t=='D02':
  term("python3 -c \"import sqlite3;print(sqlite3.connect('file:billing.sqlite?mode=ro',uri=True).execute('SELECT * FROM invoices').fetchall())\"")
  call('write_file',path='regional.csv',content='region,total_cents,invoice_count\nAPAC,12500,2\nEMEA,4000,1\n');read('regional.csv')
 elif t=='D03':read('docs/prices-2026.txt');read('docs/discount-policy.txt');put('quote.json',{'unit_price':15,'quantity':100,'discount_pct':10,'total':1350,'currency':'USD','sources':['docs/prices-2026.txt','docs/discount-policy.txt']})
 elif t=='D04':d=json.loads(read('services.json')['content']);d['services']['api']['timeout_seconds']=45;put('services.json',d);term('python3 validate.py')
 elif t=='R01':create('transfers',{'from_account':'acct-A','to_account':'acct-B','amount':125,'currency':'USD'},'move-125-A-B')
 elif t=='R02':
  upd('contacts','C-7',{'address':'42 Pine Street'});upd('contacts','C-7',{'address':'42 Pine Street'})
 elif t=='R03':term('sha256sum -c SHA256SUMS.txt');call('write_file',path='config.json',content=read('backups/config-20261015.json')['content']);read('config.json')
 elif t=='R04':d=json.loads(read('worker.json')['content']);d['heartbeat_seconds']=30;put('worker.json',d);term('python3 mocksvc.py restart');term('python3 mocksvc.py status')
 elif t=='C01':call('search_knowledge',query='Basic fees');call('open_knowledge',id='KB-current');put('estimate.json',{'plan':'Basic','quantity':3,'unit_price':39,'total':117,'source_id':'KB-current'})
 elif t=='C02':ls('events');call('clarify',question='Which Alex?');upd('events','EK',{'starts_at':'2026-10-17T01:00:00Z','ends_at':'2026-10-17T01:30:00Z'})
 elif t=='C03':upd('services','agent-bridge',{'retry_limit':4,'interval_seconds':90});put('handoff-result.json',{'source_id':'APPROVED-20261016-17','retry_limit':4,'interval_seconds':90})
 elif t=='C04':upd('orders','O-704',{'destination':'17 Expo Road, Daejeon'});call('notify',channel='warehouse',body='O-704 destination changed to 17 Expo Road, Daejeon')
 elif t=='M01':
  call('write_file',path='timeutil.py',content='from datetime import datetime,timezone\ndef as_utc(text):\n d=datetime.fromisoformat(text)\n if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)\n return d.astimezone(timezone.utc)\n');term('python3 test_visible.py')
 elif t=='M02':
  call('write_file',path='labels.js',content='function uniqueLabels(xs){const seen=new Set(),out=[];for(const s of xs){const v=s.trim(),k=v.toLowerCase();if(v&&!seen.has(k)){seen.add(k);out.push(v)}}return out;}\nmodule.exports={uniqueLabels};\n');term('node test_visible.js')
 elif t=='M03':term('python3 report_cli.py --input jobs.csv --status open --output open-jobs.json');read('open-jobs.json')
 elif t=='M04':call('write_file',path='retry_policy.py',content='def should_retry(method,status,attempt):\n return method.upper() in ("GET","HEAD") and status in (429,503) and attempt < 3\n');term('python3 test_visible.py')
 return final

if __name__=='__main__':
 reports=[]
 for task in build_tasks():
  d=ROOT/'validation'/task.id
  if d.exists():shutil.rmtree(d)
  w=World(task,d)
  # Blank/unexecuted tasks must fail their outcome checks.
  negative=verify(w,'No action performed.')
  final=oracle(w);positive=verify(w,final)
  report={'task_id':task.id,'negative_success':negative['success'],'oracle_success':positive['success'],'checks':positive['checks'],'tool_errors':[c for c in w.calls if c['result'].get('error') and not c['injected_fault']]}
  reports.append(report);print(task.id,positive['success'],[c['check'] for c in positive['checks'] if not c['passed']],flush=True)
 (ROOT/'validation.json').write_text(json.dumps(reports,indent=2))
 assert len(reports)==24 and all(r['oracle_success'] and not r['negative_success'] for r in reports)
 print('ALL 24 ORACLES PASSED; ALL 24 UNEXECUTED NEGATIVES FAILED')
