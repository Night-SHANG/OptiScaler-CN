"""Compile actual scanner/injector output for portable UI boundary regressions."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from loclib import find_candidates, key_for_source
from localize_source import instrument_file

class GeneratedUiSyntaxTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'), 'portable C++ compiler not installed')
    def test_adjacent_conditional_and_brace_title_compile_after_injection(self):
        rules = json.loads((ROOT/'Localization/scanner-rules.json').read_text())
        source = '''struct ScopedCard { explicit ScopedCard(const char*) {} };
void ScopedCollapsingHeader(const char*) {}
int main() {
    bool flag = true;
    ScopedCollapsingHeader(flag ? "Clean " "input" : "Edited " /* comment */ "output");
    ScopedCard card { "System" };
}
'''
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); path = root/'sample.cpp'; path.write_text(source)
            header = root/'localization/Localization.h'; header.parent.mkdir()
            header.write_text('#pragma once\nnamespace OptiScalerCN::Loc { inline const char* T(const char*, const char* value) { return value; } }\n')
            candidates = find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)
            self.assertEqual({c.source for c in candidates}, {'Clean input','Edited output','System'})
            instrument_file(path, 'OptiScaler/menu/menu_common.cpp', rules, {c.source:key_for_source(c.source) for c in candidates})
            result = subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(path),'-o',str(root/'sample')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            subprocess.run([str(root/'sample')],check=True)
