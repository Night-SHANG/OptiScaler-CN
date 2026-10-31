#!/usr/bin/env python3
"""Independent, fixed-source probes for UI paths missed by the previous scanner.

Run after localize_source.py. This is not a whole-program/runtime coverage claim.
"""
import argparse
import json
import re
from pathlib import Path
from loclib import LOC

MASTER_PROBES = [
    'Enable reprojection', 'Hide Averages', 'Only the current values, without the averages of FPS, frame time and upscaler time',
    'FPS Overlay Cycle', 'Unbound', 'Unknown', 'Reprojection Settings',
    'Low latency timings, whole frame: ', 'RenderSubmit', 'Upscale: ',
    'DXGI spoofing', 'Override XeFG Ratio', 'Quirks and ASI',
    'Copied to the clipboard', 'No FPS overlay code in the clipboard',
    'OptiFG (Upscaler)', 'DLSSG via Streamline', 'Frame Gen', 'Custom Tab',
    'Classic', "OptiScaler's earlier overlay: just the FPS in white, no shadow",
    'Error while compiling a shader!', "Can't init FSR FG\nAre you missing the required DLLs?",
    'You are missing the following dlls from the streamline folder:\n',
    "{} Doesn't support more than {}x", '{} off',
]

def verify(source: Path, channel: str):
    catalog = json.loads((LOC/channel/'catalog.json').read_text())['entries']
    active = {e['source']: (k,e) for k,e in catalog.items() if not e.get('obsolete')}
    zh = json.loads((LOC/'zh-CN.json').read_text())['entries']
    menu = (source/'OptiScaler/menu/menu_common.cpp').read_text()
    if channel == 'master':
        for text in MASTER_PROBES:
            assert text in active, f'uncatalogued probe: {text!r}'
            key, entry = active[text]
            assert zh[key]['text'] and zh[key]['source_hash'] == entry['source_hash'], text
        for marker in [
            '// CN FPS overlay: preserve the validated menu-font fallback.',
            'OptiScalerCN::Loc::TL(flag.description).c_str()',
            'OptiScalerCN::Loc::TL(overlayRowNames[row]).c_str()',
            'OptiScalerCN::Loc::TL(overlayRowTips[row]).c_str()',
            'OptiScalerCN::Loc::TL(box.tab).c_str()',
            'OptiScalerCN::Loc::TL(box.name) + "###" + box.name',
            'OptiScalerCN::Loc::TL(presets[i].tip).c_str()',
            'OptiScalerCN::Loc::TL(tabs[i].displayLabel',
            'strcmp(tabs[i].label, requestedMenuTab)',
        ]:
            assert marker in menu, marker
        keys = re.search(r'static const char\* overlayRowKeys\[\].*?;',menu,re.S)
        assert keys and 'OptiScalerCN' not in keys[0]
        for name in ('overlayRowNames', 'overlayRowTips'):
            raw = re.search(r'static const char\* '+name+r'\[\].*?;',menu,re.S)
            assert raw and 'OptiScalerCN' not in raw[0], name
        for name in ('Tab tabs','MenuBox boxes','OverlayPreset presets'):
            start = menu.index('static const '+name)
            end = menu.index('};',start)
            assert 'OptiScalerCN' not in menu[start:end], name
    for marker in ['OptiScalerCN::Loc::TL(opt.tooltip).c_str()',
                   'OptiScalerCN::Loc::TL(name) + "###" + name']:
        assert marker in menu, marker
    assert 'std::format(OptiScalerCN::Loc::T' not in menu
    generated = (source/'OptiScaler/localization/generated/Strings.generated.h').read_text()
    for key,entry in catalog.items():
        if not entry.get('obsolete'):
            assert f'"{key}"' in generated, key
    print(f'{channel}: fixed UI probes, translated display uses, raw contracts and generated dictionary verified')

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--channel',choices=['master','stable'],required=True)
    args=ap.parse_args();verify(args.source,args.channel)
