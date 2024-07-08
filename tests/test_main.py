import re

from typer.testing import CliRunner

from autogest.main import app, template_render, INCOME_TAX_TEMPLATE

runner = CliRunner()


def test_renta():
    # Test case 1: yield_total = 30000, tax_paid = 6000, to_deduct = 5750
    result = runner.invoke(app, ["renta", "30000", "6000", "-d", "5750"])
    kw_report = dict(yield_total=30000.0, tax_paid=6000.0, to_deduct=5750.0)
    report_str = template_render(INCOME_TAX_TEMPLATE, **kw_report, income_tax=-559.44)
    report_str = re.sub(r"\[.*?\]", "", report_str)
    assert result.exit_code == 0
    print(result.stdout)
    assert report_str in result.stdout
    # TODO: Add more test cases
    # Test case 2: yield_total = 50000, tax_paid = 10000, to_deduct = 0
    # result = runner.invoke(app, ["renta", "50000", "10000", "-d", "0"])
    # Test case 3: yield_total = 100000, tax_paid = 20000, to_deduct = 15000
    # result = runner.invoke(app, ["renta", "100000", "20000", "-d", "15000"])
