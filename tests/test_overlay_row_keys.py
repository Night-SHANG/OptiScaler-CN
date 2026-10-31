import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from loclib import find_candidates

class OverlayRowKeyTests(unittest.TestCase):
    def test_persistent_row_keys_are_not_localized_but_display_names_are(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = '''static const char* overlayRowKeys[] = { "fps", "upscale", "frametime" };
static const char* overlayRowNames[] = { "FPS", "Upscale Ratio", "Frame Time" };
ImGui::Text("fps");'''
        found = find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)
        arrays = {c.source for c in found if c.callee == 'c-string-array'}
        self.assertEqual(arrays, {'FPS', 'Upscale Ratio', 'Frame Time'})
        self.assertTrue(any(c.source == 'fps' and c.callee == 'ImGui::Text' for c in found))

    def test_overlay_display_helpers_collected_without_value_ids(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = 'line.Label(L("Upscale: ", "UPS ")).Value("upscale", value); wholeFrame.Label("Low latency timings, whole frame: ");'
        sources = {c.source for c in find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)}
        self.assertTrue({'Upscale: ', 'UPS ', 'Low latency timings, whole frame: '} <= sources)
        self.assertNotIn('upscale', sources)

    def test_timing_description_is_display_text_not_timing_value(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = 'drawTiming(timingData.driver, "Driver", ImVec4());'
        found = find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)
        self.assertEqual([c.source for c in found], ['Driver'])

    def test_menu_helper_labels_and_tooltips_not_setting_identifiers(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = '''ConfigCheckbox("Enabled option", option, "Explanation");
SectionTitle("Logging"); optionCheckbox("Hide Averages", setting, "Only current values");
scaleSlider("Label Size", setting); colorEdit("Labels", setting);
pair("Swapchain", "None"); flag("DXGI spoofing", value);'''
        found = {c.source for c in find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)}
        self.assertTrue({'Enabled option', 'Explanation', 'Logging', 'Hide Averages', 'Only current values', 'Label Size', 'Labels', 'Swapchain', 'None', 'DXGI spoofing'} <= found)

    def test_structured_display_tables_preserve_keys_and_settings(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = '''static const OverlayPreset presets[] = {{"Classic", "Earlier overlay", "Type=3;Rows=fps"}};
static const MenuBox boxes[] = {{"status_init", "Status", "Init Flags", nullptr}};
static const Tab tabs[] = {{"advanced", "Status", nullptr}};
ScopedCard card { "System" };'''
        found = find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)
        self.assertEqual({c.source for c in found}, {'Classic','Earlier overlay','Status','Init Flags','System'})
        self.assertTrue(all(not c.rewrite for c in found if c.source != 'System'))

    def test_adjacent_conditional_literals_are_single_expressions(self):
        rules = {'calls': {'ScopedCollapsingHeader':[0]}, 'conditional_literal_calls':['ScopedCollapsingHeader']}
        source = 'ScopedCollapsingHeader(flag ? "Clean " "input" : "Edited " /* comment */ "output");'
        found = find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)
        self.assertEqual([c.source for c in found], ['Clean input','Edited output'])

    def test_assigned_fg_options_and_keybind_names_reach_catalog(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = '''static std::vector<MenuOption<FGInput>> inputOptions;
inputOptions = {{ FGInput::Upscaler, "OptiFG (Upscaler)", "Upscaler must be enabled" }};
static auto key = Keybind("FPS Overlay Cycle", 12);
RenderRatioOverrideSlider("Override XeFG Ratio", setting, 4);'''
        found = find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)
        self.assertTrue({'OptiFG (Upscaler)','Upscaler must be enabled','FPS Overlay Cycle','Override XeFG Ratio'} <= {c.source for c in found})
        self.assertTrue(all(not c.rewrite for c in found if c.callee == 'Keybind'))

    def test_dynamic_display_status_and_return_expressions(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = '''settingsCodeStatus = "Copied to the clipboard";
auto modeName = [&](int mode) -> std::string { if(mode == 0) return "Off"; return "On"; };
auto formatFg = [&](int n) { return std::format("{} off", n); };
static const char* QuirksTabLabel(State& state) { return "Quirks and ASI"; }
'''
        found = find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)
        self.assertTrue({'Copied to the clipboard', 'Off', 'On', '{} off','Quirks and ASI'} <= {c.source for c in found})
        self.assertEqual([c.callee for c in found if c.source == '{} off'], ['nested:std::format'])

    def test_conditional_toast_method_and_layout_measurement(self):
        rules = json.loads((ROOT / 'Localization/scanner-rules.json').read_text())
        source = 'toast.setContent(ok ? "Works" : "Failed"); ImGui::CalcTextSize("Use Value");'
        found = {c.source for c in find_candidates(source, 'OptiScaler/menu/menu_common.cpp', rules)}
        self.assertTrue({'Works','Failed','Use Value'} <= found)
