#!/usr/bin/env python3
from __future__ import annotations
import argparse, difflib, subprocess
from pathlib import Path
from loclib import *

def git_sha(root: Path):
    try: return subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    except Exception: return ''

@dataclass
class ReconcileResult:
    catalog_entries: dict
    zh_entries: dict
    added: list[str]
    changed: list[tuple[str,str,str]]
    removed: list[str]
    missing: list[str]
    stale: list[str]


def reconcile(found: list[Candidate], old_entries: dict, zh: dict, tm: dict) -> ReconcileResult:
    """Reconcile a fresh UI inventory with stable keys and existing translations."""
    old_by_source={v.get('source'):k for k,v in old_entries.items() if not v.get('obsolete')}
    old_by_scope={}
    for k,v in old_entries.items():
        for o in v.get('occurrences',[]):
            old_by_scope.setdefault((o.get('file'),o.get('callee')),[]).append((k,v))

    entries={k:{**v,'occurrences':[]} for k,v in old_entries.items()}
    used=set(); added=[]; changed=[]
    for c in found:
        key=old_by_source.get(c.source)
        if key is None:
            best=None; best_ratio=0.0
            for k,v in old_by_scope.get((c.file,c.callee),[]):
                if k in used or v.get('obsolete'): continue
                r=difflib.SequenceMatcher(None,v.get('source',''),c.source).ratio()
                if r>best_ratio: best_ratio=r; best=(k,v)
            if best and best_ratio>=0.84:
                key=best[0]
                prev=entries[key].get('source','')
                if prev!=c.source:
                    entries[key].setdefault('previous_sources',[])
                    if prev and prev not in entries[key]['previous_sources']: entries[key]['previous_sources'].append(prev)
                    entries[key]['source']=c.source
                    entries[key]['source_hash']=sha(c.source)
                    changed.append((key,prev,c.source))
            else:
                key=key_for_source(c.source)
                suffix=1; base=key
                while key in entries and entries[key].get('source')!=c.source:
                    suffix+=1; key=f'{base}.{suffix}'
                if key not in entries:
                    entries[key]={'source':c.source,'source_hash':sha(c.source),'occurrences':[],'obsolete':False,'previous_sources':[]}
                    added.append(key)
        used.add(key)
        e=entries[key]; e['source']=c.source; e['source_hash']=sha(c.source); e['obsolete']=False
        occurrence={'file':c.file,'line':c.line,'callee':c.callee,'arg':c.arg_index}
        if occurrence not in e['occurrences']:
            e['occurrences'].append(occurrence)

    removed=[]
    for k,e in entries.items():
        if k not in used and not e.get('obsolete'):
            e['obsolete']=True; removed.append(k)

    current={k:e for k,e in entries.items() if not e.get('obsolete')}
    zentries={k:dict(v) for k,v in zh.get('entries',{}).items()}
    for k,e in current.items():
        z=zentries.get(k)
        if z is None and e['source'] in tm:
            zentries[k]={'text':tm[e['source']],'state':'reviewed','source_hash':e['source_hash'],'note':'seeded from maintained translation memory'}

    missing=[]; stale=[]
    for k,e in current.items():
        z=zentries.get(k)
        if not z or not z.get('text'):
            missing.append(k)
        elif z.get('source_hash')!=e['source_hash']:
            stale.append(k)
    return ReconcileResult(entries,zentries,added,changed,removed,missing,stale)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--update',action='store_true')
    ap.add_argument('--report',type=Path,default=ROOT/'reports'/'localization-scan.md')
    args=ap.parse_args()
    rules=load_json(LOC/'scanner-rules.json',{})
    old=load_json(LOC/'catalog.json',{'schema':1,'entries':{}})
    en=load_json(LOC/'en-US.json',{'locale':'en-US','entries':{}})
    zh=load_json(LOC/'zh-CN.json',{'locale':'zh-CN','entries':{}})
    tm=load_json(LOC/'translation-memory.zh-CN.json',{})
    old_entries=old.get('entries',{})

    found=[]
    for p in iter_source_files(args.source,rules):
        rel=p.relative_to(args.source).as_posix()
        text=p.read_text(encoding='utf-8-sig',errors='replace')
        found.extend(find_candidates(text,rel,rules))

    result=reconcile(found, old_entries, zh, tm)
    entries=result.catalog_entries
    zentries=result.zh_entries
    added=result.added
    changed=result.changed
    removed=result.removed
    missing=result.missing
    stale=result.stale
    current={k:e for k,e in entries.items() if not e.get('obsolete')}
    en_entries={k:{'text':e['source'],'source_hash':e['source_hash']} for k,e in current.items()}

    pending={
      'locale':'zh-CN',
      'scan':{'added':added,'changed':[k for k,_,_ in changed],'removed':removed},
      'missing':[{'key':k,'source':current[k]['source'],'source_hash':current[k]['source_hash']} for k in missing],
      'changed':[{'key':k,'source':current[k]['source'],'source_hash':current[k]['source_hash'],'old_translation':zentries.get(k,{}).get('text',''),'state':zentries.get(k,{}).get('state','')} for k in stale]
    }
    commit=git_sha(args.source)
    catalog={'schema':1,'upstream_commit':commit,'entries':entries}
    coverage=(len(current)-len(missing)-len(stale))/len(current)*100 if current else 100.0
    report=[
      '# Localization scan report','',f'- Upstream commit: `{commit or "unknown"}`',
      f'- Active UI strings: **{len(current)}**',f'- Added: **{len(added)}**',f'- Removed: **{len(removed)}**',
      f'- Source changed / translation stale: **{len(stale)}**',f'- Missing zh-CN: **{len(missing)}**',f'- Effective zh-CN coverage: **{coverage:.2f}%**',''
    ]
    if added: report += ['## Added','']+[f'- `{k}` — {current[k]["source"]!r}' for k in added[:100]]+['']
    if stale: report += ['## Changed / stale','']+[f'- `{k}` — {current[k]["source"]!r}' for k in stale[:100]]+['']
    if removed: report += ['## Removed','']+[f'- `{k}`' for k in removed[:100]]+['']
    args.report.parent.mkdir(parents=True,exist_ok=True); args.report.write_text('\n'.join(report)+'\n',encoding='utf-8')
    if args.update:
        save_json(LOC/'catalog.json',catalog)
        save_json(LOC/'en-US.json',{'locale':'en-US','entries':en_entries})
        save_json(LOC/'zh-CN.json',{'locale':'zh-CN','entries':zentries})
        save_json(LOC/'pending.json',pending)
    print(f'active={len(current)} added={len(added)} removed={len(removed)} missing={len(missing)} stale={len(stale)} coverage={coverage:.2f}%')

if __name__=='__main__': main()
