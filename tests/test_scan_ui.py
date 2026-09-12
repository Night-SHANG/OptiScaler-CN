import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import scan_ui
from loclib import Candidate, sha

class ScanUiTests(unittest.TestCase):
    def c(self, source, line=1, callee='ImGui::Text'):
        return Candidate('OptiScaler/menu/menu_common.cpp',callee,0,source,0,1,line,'"x"',True)

    def test_exact_source_keeps_existing_key_and_reviewed_translation(self):
        old={'ui.custom.quality':{'source':'Quality','source_hash':sha('Quality'),'occurrences':[{'file':'OptiScaler/menu/menu_common.cpp','callee':'ImGui::Text'}],'obsolete':False,'previous_sources':[]}}
        zh={'locale':'zh-CN','entries':{'ui.custom.quality':{'text':'质量','state':'reviewed','source_hash':sha('Quality')}}}
        result=scan_ui.reconcile([self.c('Quality')], old, zh, {'Quality':'质量'})
        self.assertIn('ui.custom.quality',result.catalog_entries)
        self.assertEqual(result.zh_entries['ui.custom.quality']['text'],'质量')
        self.assertEqual(result.missing,[])

    def test_changed_source_keeps_key_but_marks_reviewed_translation_stale(self):
        old={'ui.custom.apply':{'source':'Apply changes','source_hash':sha('Apply changes'),'occurrences':[{'file':'OptiScaler/menu/menu_common.cpp','callee':'ImGui::Text'}],'obsolete':False,'previous_sources':[]}}
        zh={'locale':'zh-CN','entries':{'ui.custom.apply':{'text':'应用更改','state':'reviewed','source_hash':sha('Apply changes')}}}
        result=scan_ui.reconcile([self.c('Apply changes now')], old, zh, {})
        self.assertEqual(result.catalog_entries['ui.custom.apply']['source'],'Apply changes now')
        self.assertEqual(result.stale,['ui.custom.apply'])
        self.assertEqual(result.zh_entries['ui.custom.apply']['text'],'应用更改')

    def test_translation_memory_seeds_new_exact_source(self):
        result=scan_ui.reconcile([self.c('Balanced')], {}, {'locale':'zh-CN','entries':{}}, {'Balanced':'均衡'})
        key=next(iter(result.catalog_entries))
        self.assertEqual(result.zh_entries[key]['state'],'reviewed')
        self.assertEqual(result.zh_entries[key]['text'],'均衡')
        self.assertEqual(result.missing,[])

    def test_removed_entry_becomes_obsolete(self):
        old={'ui.old':{'source':'Gone','source_hash':sha('Gone'),'occurrences':[],'obsolete':False,'previous_sources':[]}}
        result=scan_ui.reconcile([], old, {'locale':'zh-CN','entries':{}}, {})
        self.assertTrue(result.catalog_entries['ui.old']['obsolete'])
        self.assertEqual(result.removed,['ui.old'])

if __name__ == '__main__':
    unittest.main()
