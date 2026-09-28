"""Recalculate released tables from judgments; no inference and no hidden inputs."""
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import socket
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
# Calculation must remain offline even if an optional dependency tries a connection.
def no_network(*args,**kwargs):raise RuntimeError('Network disabled during statistical reproduction')
socket.socket.connect=no_network
socket.create_connection=no_network
from src.statistics import compute_stats, render_report, winrate_with_ci
from src.consensus import batch_kappa, render_kappa_md, pairwise_majority
from src.heldout import report as heldout_report

def readl(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def dump(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def equal(a,b,path=''):
 if isinstance(a,dict):
  assert isinstance(b,dict) and set(a)==set(b),(path,'keys')
  for k in a:equal(a[k],b[k],path+'/'+k)
 elif isinstance(a,(list,tuple)):
  assert isinstance(b,(list,tuple)) and len(a)==len(b),(path,'length')
  for i,(x,y) in enumerate(zip(a,b)):equal(x,y,path+'/'+str(i))
 elif isinstance(a,float):assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) or math.isnan(a) and math.isnan(b),(path,a,b)
 else:assert a==b,(path,a,b)

def main():
 manifest=json.loads((ROOT/'MANIFEST.json').read_text())
 for name,expected in manifest['files'].items():
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,('checksum',name)
 data=ROOT/'data';out=ROOT/'outputs';out.mkdir(exist_ok=True)
 J=readl(data/'judgments.jsonl');P=readl(data/'pairwise.jsonl');idx=readl(data/'session_index.jsonl');sample=readl(data/'transcripts_sample_300.jsonl')
 assert len(J)==len(idx)==2250 and len(P)==1800 and len(sample)==300
 assert len({j['session_id'] for j in J})==2250
 assert {j['session_id'] for j in J}=={r['session_id'] for r in idx}
 assert all(len(j['per_judge'])==3 for j in J)
 for p in P:assert pairwise_majority([v.get('winner') for v in p['votes']])[0]==p['winner']
 stats=compute_stats(J,P);expected=json.loads((ROOT/'reference/stats.json').read_text())
 for k in stats:equal(stats[k],expected[k],'/stats/'+k)
 consensus=batch_kappa(J);equal(consensus,json.loads((ROOT/'reference/consensus.json').read_text()),'/consensus')
 dump(out/'stats.json',stats);dump(out/'consensus.json',consensus)
 (out/'tables_main.md').write_text(render_report(stats,None)+'\n'+render_kappa_md(consensus))
 # Holdout function writes only beneath outputs; input copies are all public records.
 hd=out/'heldout';hd.mkdir(exist_ok=True)
 (out/'pairwise.jsonl').write_bytes((data/'pairwise.jsonl').read_bytes())
 (hd/'pairwise_heldout.jsonl').write_bytes((data/'heldout/pairwise_heldout.jsonl').read_bytes())
 h=heldout_report(out,('C3','C4'),'google/gemini-3.1-pro',log=lambda _:None)
 href=json.loads((ROOT/'reference/heldout/heldout_report.json').read_text())
 metadata_differences={}
 if h['resolved_model']!=href['resolved_model']:
  metadata_differences['heldout.resolved_model']={'raw_record':h['resolved_model'],'stored_summary':href['resolved_model']}
 equal({k:v for k,v in h.items() if k!='resolved_model'},{k:v for k,v in href.items() if k!='resolved_model'},'/heldout')
 branch={r['meta']['persona_id']:r['branch'] for r in idx};splits=[]
 for b in sorted(set(branch.values())):
  rows=[p for p in P if p['pair']==['C2','C3'] and branch[p['persona_id']]==b];c=Counter(r['winner'] for r in rows)
  splits.append({'branch':b,'total_pairs':len(rows),'a_wins':c['A'],'b_wins':c['B'],'ties':c['tie'],**winrate_with_ci(rows,'C2','C3')})
 equal(splits,json.loads((ROOT/'reference/v020/c2_c3_by_branch.json').read_text()),'/branch')
 # Sampling: every condition x branch x behavior cell contributes two of fifteen.
 strata=defaultdict(list)
 for r in idx:strata[(r['meta']['condition'],r['branch'],r['behavior'])].append(r)
 expected_ids=set()
 for rows in strata.values():
  assert len(rows)==15
  expected_ids.update(r['session_id'] for r in sorted(rows,key=lambda r:hashlib.sha256(('release-v0.2.2|'+r['session_id']).encode()).hexdigest())[:2])
 assert len(strata)==150 and {r['session_id'] for r in sample}==expected_ids
 # Remaining post-hoc tables are calculated from coded rows/numeric event records.
 gpts=[v for j in J for v in j['per_judge'] if v['judge_model']=='openai/gpt-5.4'];empty=[v for v in gpts if not (v.get('rationale') or '').strip()]
 assert len(empty)==918 and all(not any(v['failures_llm'].values()) for v in empty)
 annotations=readl(data/'rationale_annotations.jsonl');assert len(annotations)==918 and all(not a['is_original_model_rationale'] for a in annotations)
 m=json.loads((data/'s6_mapping_codes.json').read_text());c=Counter(r['classification'] for r in m);nf=sum(r['primary_code'].startswith('F') for r in m)
 assert len(m)==234 and len({r['row_id'] for r in m})==234
 s6={'total':len(m),'class_counts':dict(c),'behavior_rows':nf,'mapping_coverage':(c['seed_and_rubric']+c['rubric_only'])/nf,'direct_seed_coverage':c['seed_and_rubric']/nf}
 assert c=={'seed_and_rubric':52,'rubric_only':2,'out_of_scope_ui':88,'out_of_scope_other':92}
 index={r['session_id']:r for r in idx};events=readl(data/'f1_events_numeric.jsonl');hitids={e['session_id'] for e in events}
 assert hitids=={j['session_id'] for j in J if j['failures']['F1']}
 c4=[e for e in events if e['condition']=='C4'];patterns=[]
 for i in range(1,11):
  es=[e for e in c4 if e['pattern_id']==f'F1-P{i:02d}'];patterns.append({'pattern_id':f'F1-P{i:02d}','sessions':len({e['session_id'] for e in es}),'turn_pattern_hits':len(es)})
 cross=[];behavior=[]
 for (b,pid,bh) in sorted({(r['branch'],r['meta']['persona_id'],r['behavior']) for r in idx if r['meta']['condition']=='C4'}):
  for i in range(1,11):
   es=[e for e in c4 if e['persona_id']==pid and e['pattern_id']==f'F1-P{i:02d}']
   cross.append({'branch':b,'persona_id':pid,'behavior':bh,'pattern_id':f'F1-P{i:02d}','n_sessions':3,'f1_sessions':len({e['session_id'] for e in es}),'hits':len(es)})
 for bh in sorted({r['behavior'] for r in idx}):
  rows=[j for j in J if j['meta']['condition']=='C4' and index[j['session_id']]['behavior']==bh];n=sum(j['failures']['F1'] for j in rows)
  behavior.append({'behavior':bh,'n':len(rows),'f1_sessions':n,'rate':n/len(rows)})
 dump(out/'c4_f1_branch_persona_pattern.json',cross)
 f1=[]
 for condition in ['C3','C4']:
  for b in sorted(set(branch.values())):
   rows=[j for j in J if j['meta']['condition']==condition and j['branch']==b];n=sum(j['failures']['F1'] for j in rows)
   f1.append({'condition':condition,'branch':b,'n':len(rows),'f1_sessions':n,'rate':n/len(rows)})
 ref=json.loads((ROOT/'reference/v020/summary.json').read_text());equal(f1,ref['f1_branch'],'/F1');equal(behavior,ref['c4_f1_behavior'],'/behavior')
 for x,y in zip(patterns,ref['c4_f1_patterns']):
  for key in x:equal(x[key],y[key],'/patterns/'+key)
 log=readl(data/'learning_curve.jsonl');lc={'iterations':len(log),'best_initial':log[0]['best_so_far'],'best_final':log[-1]['best_so_far'],'gate_fail_count':sum(not r.get('gate_passed',True) for r in log),'plateau_final':bool(log[-1].get('plateau',False)),'since_improve_final':log[-1].get('since_improve')}
 for k,v in lc.items():equal(v,expected['learning_curve'][k],'/learning/'+k)
 coverage={c:sum(j['coverage'] for j in J if j['meta']['condition']==c)/450 for c in stats['conditions']}
 posthoc={'f1_branch':f1,'c4_f1_patterns':patterns,'gpt_rationale_empty':len(empty),'rationale_annotations':len(annotations),'s6':s6,'c2_c3_by_branch':splits,'learning_curve':lc,'coverage':coverage}
 dump(out/'tables_supplement.json',posthoc)
 audit={'checksums':len(manifest['files']),'judgments':len(J),'per_judge':len(gpts)*3,'pairwise':len(P),'transcripts':len(sample),'strata':len(strata),'all_published_reference_statistics_match':True,'api_calls':0,'manuscript_section_mapping':'pending exact manuscript','p5':'not performed','metadata_discrepancies':metadata_differences}
 dump(out/'verification.json',audit)
 print(json.dumps(audit,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
