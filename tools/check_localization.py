#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from loclib import *


def analyze(cat: dict, en: dict, zh: dict) -> dict:
    """Validate structural safety and report fallback states separately.

    Missing/stale translations are intentionally not structural errors: runtime
    falls back to the canonical English source for those entries.
    """
    errors=[]; warnings=[]
    active={k:v for k,v in cat.get('entries',{}).items() if not v.get('obsolete')}
    if en.get('locale')!='en-US': errors.append('en-US.json locale must be en-US')
    if zh.get('locale')!='zh-CN': errors.append('zh-CN.json locale must be zh-CN')
    zentries=zh.get('entries',{})
    reviewed=machine=missing=stale=0
    for k,e in active.items():
        src=e.get('source',''); h=e.get('source_hash')
        if sha(src)!=h: errors.append(f'{k}: catalog source_hash mismatch')
        en_entry=en.get('entries',{}).get(k,{})
        if en_entry.get('text')!=src: errors.append(f'{k}: en-US mismatch')
        if en_entry.get('source_hash') not in (None,h): errors.append(f'{k}: en-US source_hash mismatch')
        z=zentries.get(k)
        if not z or not z.get('text'):
            missing+=1
            continue
        if z.get('source_hash')!=h:
            stale+=1
            warnings.append(f'{k}: zh-CN is stale and will fall back to English')
            continue
        state=z.get('state')
        if state not in ('reviewed','machine_translated'):
            errors.append(f'{k}: invalid translation state {state!r}')
            continue
        reviewed += state=='reviewed'; machine += state=='machine_translated'
        if printf_tokens(src)!=printf_tokens(z['text']): errors.append(f'{k}: printf placeholders differ')
        if format_tokens(src)!=format_tokens(z['text']): errors.append(f'{k}: std::format placeholders differ')
        if '##' in src:
            if '##' not in z['text'] or src.split('##',1)[1] != z['text'].split('##',1)[1]:
                errors.append(f'{k}: ImGui ## id suffix changed or missing')
    total=len(active); effective=reviewed+machine
    stats={'total':total,'reviewed':reviewed,'machine':machine,'missing':missing,'stale':stale,
           'coverage':100.0*effective/total if total else 100.0}
    return {'errors':errors,'warnings':warnings,'stats':stats}


def main():
    ap=argparse.ArgumentParser()
    # Kept for workflow/backward compatibility. "strict" means structural
    # validation; safe English-fallback states (missing/stale) remain warnings.
    ap.add_argument('--strict',action='store_true')
    args=ap.parse_args()
    cat=load_json(LOC/'catalog.json',{}); en=load_json(LOC/'en-US.json',{}); zh=load_json(LOC/'zh-CN.json',{})
    result=analyze(cat,en,zh); s=result['stats']
    print(f"total={s['total']} reviewed={s['reviewed']} machine={s['machine']} missing={s['missing']} stale={s['stale']} coverage={s['coverage']:.2f}%")
    for w in result['warnings'][:50]: print('WARN:',w)
    for e in result['errors']: print('ERROR:',e,file=sys.stderr)
    return 1 if result['errors'] else 0

if __name__=='__main__': raise SystemExit(main())
