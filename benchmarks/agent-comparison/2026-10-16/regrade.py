"""Symmetric post-run verification audit; never calls either model or changes timings."""
import copy, dataclasses, hashlib,json,tempfile
from pathlib import Path
from suite import World,build_tasks,verify
ROOT=Path(__file__).resolve().parent

def main():
 tasks={t.id:t for t in build_tasks()}
 manifest=json.loads((ROOT/'task-manifest.json').read_text())
 assert json.loads(json.dumps([dataclasses.asdict(t) for t in tasks.values()],ensure_ascii=False))==manifest,'Task definitions changed'
 paths=sorted((ROOT/'runs').glob('*/*/result.json'));assert len(paths)==144,len(paths)
 audit=[];all_rows=[]
 for p in paths:
  before=json.loads(p.read_text());tr=json.loads((p.parent/'trajectory.json').read_text());task=tasks[before['task_id']]
  with tempfile.TemporaryDirectory(prefix='agent-grader-state-') as td:
   world=World(task,td)
   world.root=p.parent/'workspace';world.db=copy.deepcopy(tr['state']);world.calls=tr['tool_calls'];world.audit=tr['audit'];world.notifications=tr['notifications']
   if any(c['injected_fault'] and c['result'].get('error')=='TIMEOUT' for c in world.calls):world.faults['timeout_after_commit']=True
   if any(c['injected_fault'] and c['result'].get('error')=='VERSION_CONFLICT' for c in world.calls):world.faults['version_conflict']=True
   scored=verify(world,before['final_response'])
  after={**before,'checks':scored['checks'],'partial_score':scored['partial_score'],'success':scored['success'] and before['stop_reason']=='final_response','failed_checks':[c['check'] for c in scored['checks'] if not c['passed']]}
  if not (p.parent/'result-original.json').exists():(p.parent/'result-original.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
  p.write_text(json.dumps(after,ensure_ascii=False,indent=2));all_rows.append(after)
  if before['success']!=after['success'] or before['failed_checks']!=after['failed_checks']:
   audit.append({'model':before['model'],'task':before['task_id'],'trial':before['trial'],'before_success':before['success'],'after_success':after['success'],'before_failed_checks':before['failed_checks'],'after_failed_checks':after['failed_checks']})
 for model in ('glm','qwen'):(ROOT/f'{model}-results.json').write_text(json.dumps([r for r in all_rows if r['model']==model],ensure_ascii=False,indent=2))
 (ROOT/'results.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in all_rows))
 (ROOT/'grading-audit.json').write_text(json.dumps({'episodes_regraded':len(all_rows),'changed':audit,'model_timings_unchanged':True,'task_definitions_unchanged':True},ensure_ascii=False,indent=2))
 meta=json.loads((ROOT/'metadata.json').read_text());meta['final_grader_sha256']=hashlib.sha256((ROOT/'suite.py').read_bytes()).hexdigest();meta['grading_audit']='grading-audit.json';(ROOT/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 print('REGRADE COMPLETE',len(all_rows),'episodes;',len(audit),'verification verdict changes');print(json.dumps(audit,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
