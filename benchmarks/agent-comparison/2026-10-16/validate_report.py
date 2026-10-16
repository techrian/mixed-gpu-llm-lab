"""Validate workbook generation with synthetic records outside scored data."""
import copy,json,tempfile
from pathlib import Path
import report
real=report.ROOT
with tempfile.TemporaryDirectory(prefix='agent-report-validation-') as td:
 root=Path(td);(root/'snapshots').mkdir()
 for name in ['metadata.json','task-manifest.json','validation.json']:(root/name).write_bytes((real/name).read_bytes())
 tasks=json.loads((root/'task-manifest.json').read_text());checks=json.loads((root/'validation.json').read_text())
 for m in ('qwen','glm'):
  cfg=json.loads((real/'snapshots'/f'{m}-original-config.json').read_text())
  (root/'snapshots'/f'{m}-original-config.json').write_text(json.dumps(cfg))
  (root/'snapshots'/f'{m}-health.json').write_text(json.dumps({'version':'SYNTHETIC-VALIDATION'}))
  (root/'snapshots'/f'{m}-metrics.json').write_text(json.dumps({'engine':{},'gpu_map':[]}))
  for t in tasks:
   for trial in range(1,4):
    dest=root/'runs'/m/(t['id']+f'-r{trial}');dest.mkdir(parents=True)
    r={'model':m,'task_id':t['id'],'title':t['title'],'category':t['category'],'trial':trial,'success':True,'partial_score':1,'checks':next(x['checks'] for x in checks if x['task_id']==t['id']),
      'wall_s':10,'first_tool_s':1,'llm_s':9,'tool_s':1,'turns':2,'tool_calls':1,'schema_valid_calls':1,'tool_errors':0,'injected_faults':0,'ttft_s':[1.0], 'stop_reason':'final_response','usage':{'prompt_tokens':100,'completion_tokens':50,'cached_prompt_tokens':0},'errors':[],'final_response':'SYNTHETIC VALIDATION ONLY','run_path':str(dest),'failed_checks':[]}
    tr={'trace':[{'response':{'usage':{'prompt_tokens':100}}}],'tool_calls':[{'name':'read_file','arguments':{'path':'synthetic.txt'},'schema_valid':True,'injected_fault':False,'result':{'content':'test'},'wall_s':1}]}
    (dest/'result.json').write_text(json.dumps(r));(dest/'trajectory.json').write_text(json.dumps(tr))
 report.ROOT=root;report.create_report()
print('SYNTHETIC WORKBOOK VALIDATION PASSED; TEMPORARY FILES REMOVED')
