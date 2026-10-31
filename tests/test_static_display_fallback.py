"""Generated FPS table use must honor font failure after static initialization."""
import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from loclib import find_candidates,key_for_source
from localize_source import instrument_file,patch_dynamic_helpers

class StaticDisplayFallbackTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'),'C++ compiler unavailable')
    def test_actual_injection_refreshes_labels_and_tips_after_font_failure(self):
        source='''#include "localization/Localization.h"
#include <string>
#include <cassert>
static const char* overlayRowNames[] = { "Frame Time" };
static const char* overlayRowTips[] = { "Explanation" };
std::string label,tip;
namespace ImGui { bool Checkbox(const char* s,bool*) {label=s;return false;} }
void ShowTooltip(const char* s) {tip=s;}
void draw() { int row=0; bool rowOn=true;
ImGui::Checkbox(overlayRowNames[row], &rowOn);
ShowTooltip(overlayRowTips[row]); }
int main() {draw(); assert(label=="中文"); assert(tip=="中文");
OptiScalerCN::Loc::active=false;
draw(); assert(label=="Frame Time"); assert(tip=="Explanation"); }
'''
        rules=json.loads((ROOT/'Localization/scanner-rules.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'sample.cpp';path.write_text(source)
            h=Path(td)/'localization/Localization.h';h.parent.mkdir()
            h.write_text('#pragma once\n#include <string>\nnamespace OptiScalerCN::Loc { inline bool active=true; inline const char* T(const char*,const char* s){return active?"中文":s;} inline std::string TL(const char* s){return active?"中文":s;} }\n')
            found=find_candidates(source,'OptiScaler/menu/menu_common.cpp',rules)
            instrument_file(path,'OptiScaler/menu/menu_common.cpp',rules,{c.source:key_for_source(c.source) for c in found})
            patch_dynamic_helpers(path)
            result=subprocess.run(['c++','-std=c++17',str(path),'-o',str(Path(td)/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            result=subprocess.run([str(Path(td)/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_changed_display_anchor_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'menu.cpp'
            p.write_text('static const char* overlayRowNames[] = { "FPS" }; changedDraw(overlayRowNames);')
            with self.assertRaisesRegex(RuntimeError, 'missing draw-time adapter'):
                patch_dynamic_helpers(p)
