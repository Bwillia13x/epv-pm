from datetime import date
import pytest

try:
    from src.analysis.report_generator import ProfessionalReportGenerator, ComplianceInfo  # type: ignore
except NameError:  # HexColor missing due to ReportLab absence
    pytest.skip("ReportLab not installed", allow_module_level=True)

# Patch missing HexColor when ReportLab unavailable
import sys
module = sys.modules.get('src.analysis.report_generator')
if module and not hasattr(module, 'HexColor'):
    module.HexColor = lambda _color: _color  # type: ignore

def test_default_templates():
    compliance = ComplianceInfo(
        analyst_name="Test Analyst",
        analyst_credentials="CFA",
        firm_name="Test Firm",
        report_date=date.today(),
    )
    gen = ProfessionalReportGenerator(compliance)
    templates = gen._create_default_templates()

    # Should have both institutional and executive templates
    assert "institutional" in templates
    assert "executive" in templates

    inst = templates["institutional"]
    exec_tpl = templates["executive"]

    # basic sanity on styles
    for tpl in (inst, exec_tpl):
        assert tpl.title_style["fontSize"] > 0
        assert "primary" in tpl.color_scheme