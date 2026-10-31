import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import localize_source

class OverlayFontTests(unittest.TestCase):
    def test_overlay_font_uses_validated_cjk_ranges_without_changing_english_path(self):
        source='''static void UpdateOverlayFont() {
ImFontConfig fontConfig;
fontConfig.GlyphExtraAdvanceX = letterSpacing;
if (!wanted.empty()) { originalFontPath(); }
}
'''
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'menu.cpp';p.write_text(source)
            localize_source.patch_overlay_font(p)
            out=p.read_text()
            self.assertIn('OptiScalerCN::Loc::IsChineseActive()',out)
            self.assertIn('OptiScalerCN::Loc::ResolveChineseFont',out)
            self.assertIn('OptiScalerCN::Loc::BuildGlyphRanges(io.Fonts)',out)
            self.assertIn('if (!wanted.empty()) { originalFontPath(); }',out)
            localize_source.patch_overlay_font(p)
            self.assertEqual(out,p.read_text())
    def test_missing_optional_overlay_font_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'menu.cpp';p.write_text('stable menu')
            localize_source.patch_overlay_font(p)
            self.assertEqual(p.read_text(),'stable menu')
    def test_present_overlay_font_with_unknown_anchor_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'menu.cpp';p.write_text('static void UpdateOverlayFont() { changed(); }')
            with self.assertRaises(RuntimeError):localize_source.patch_overlay_font(p)
