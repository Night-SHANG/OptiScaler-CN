import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from localize_source import patch_dynamic_helpers

class DisplayTableIntegrationTests(unittest.TestCase):
    def test_translate_display_uses_without_rewriting_raw_table_data(self):
        source = '''ImGui::Button(name.c_str());
static const Tab tabs[] = {{"advanced", "Status", nullptr}};
if (strcmp(tabs[i].label, requestedMenuTab) == 0) selectedMenuTab = i;
ImGui::Button(presets[i].name, ImVec2(buttonWidth, 0.0f));
ShowTooltip(presets[i].tip);
ImGui::TextDisabled("%s", box.tab);
ImGui::TextDisabled(OptiScalerCN::Loc::T("format", "%s"), box.tab);
ImGui::SetTooltip(OptiScalerCN::Loc::T("format", "%s"), opt.tooltip.c_str());
ImGui::SetTooltip(OptiScalerCN::Loc::T("format", "%s"), flag.description.c_str());
ImGui::BeginTable(box.tab, 2);
ImGui::Checkbox(box.name, &on);
tabs[i].displayLabel != nullptr ? tabs[i].displayLabel(ctx) : tabs[i].label);
'''
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'menu.cpp'; p.write_text(source)
            patch_dynamic_helpers(p)
            result = p.read_text()
            self.assertIn('OptiScalerCN::Loc::TL(name) + "###" + name', result)
            self.assertIn('ShowTooltip(OptiScalerCN::Loc::TL(presets[i].tip).c_str())', result)
            self.assertIn('OptiScalerCN::Loc::TL(box.name)', result)
            self.assertEqual(result.count('OptiScalerCN::Loc::TL(box.tab)'), 2)
            self.assertIn('OptiScalerCN::Loc::TL(tabs[i].displayLabel', result)
            self.assertIn('OptiScalerCN::Loc::TL(opt.tooltip).c_str()', result)
            self.assertIn('OptiScalerCN::Loc::TL(flag.description).c_str()', result)
            self.assertIn('strcmp(tabs[i].label, requestedMenuTab)', result)
            self.assertIn('ImGui::BeginTable(box.tab, 2)', result)
            self.assertIn('static const Tab tabs[] = {{"advanced", "Status", nullptr}};', result)
            patch_dynamic_helpers(p)
            self.assertEqual(p.read_text(), result)
