from collections import OrderedDict
from pathlib import Path
from typing import Annotated

from jinja2 import Template
import typer
from rich import print

from autogest.config import TEMPLATES_DIR

app = typer.Typer(no_args_is_help=True, rich_markup_mode="markdown")


INCOME_TAX_TEMPLATE = TEMPLATES_DIR / "income_tax.jinja2"
TAX_RATES = OrderedDict(
    {
        12450: 0.19,
        20199: 0.24,
        35199: 0.30,
        59999: 0.37,
        299999: 0.45,
    }
)
EXCESS_TAX_RATE = 0.47


def file_type_callback(value: Path | None, file_type: str):
    if value and value.suffix != f".{file_type}":
        raise typer.BadParameter(f"Only {file_type.upper()} files are supported")
    return value


def template_render(template_path: Path, **kwargs):
    with open(template_path, "r") as file:
        template = Template(file.read())
    return template.render(kwargs)


@app.callback()
def callback():
    """
    **Autogest** is a CLI tool for managing your personal finances in Spain. :moneybag::spain:
    """
    pass


@app.command(epilog="Example: autogest deductions facturas.csv 6000 -d 5750")
def deductions(
    invoices_path: Annotated[
        Path,
        typer.Argument(
            help="Path to the csv with the invoices data.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
            callback=lambda x: file_type_callback(x, "csv"),
        ),
    ],
    extra_deductions: Annotated[
        float,
        typer.Option(
            "--to-deduct",
            "-d",
            help="The amount of money to deduct from the total yield.",
        ),
    ] = 0.0,
):
    """
    Calculate the **deductions** for a list of **invoices**.

    :param invoices_path: the path to the csv with the invoices data
    :param extra_deductions: the extra amount of money to deduct from the total yield
    :return: the deductions for the invoices
    """
    raise NotImplementedError("This feature is not implemented yet.")


@app.command(epilog="Example: autogest renta 30000 6000 -d 5750")
def renta(
    yield_total: Annotated[
        float,
        typer.Argument(
            help="The total yield to calculate the income tax for.",
            show_default=False,
        ),
    ],
    tax_paid: Annotated[
        float,
        typer.Argument(
            help="The amount of tax already paid.",
            show_default=False,
        ),
    ],
    to_deduct: Annotated[
        float,
        typer.Option(
            "--to-deduct",
            "-d",
            help="The amount of money to deduct from the total yield.",
        ),
    ] = 0.0,
):
    """
    Calculate the **year** income **tax** for a net yield using the **Spanish income tax brackets**.

    :param yield_net: the net yield to calculate the tax for
    :param tax_paid: the amount of tax already paid
    :return: the income tax for the yield
    """
    yield_net = round(yield_total, 2) - round(to_deduct, 2)
    income_tax = 0.0
    previous_limit = 0
    tax_rates_items = sorted(TAX_RATES.items())
    for limit, rate in tax_rates_items:
        if yield_net > limit:  # tax the income within the current section's limit
            income_tax += (limit - previous_limit) * rate
            previous_limit = limit
        else:  # tax the remaining income withing the current section
            income_tax += (yield_net - previous_limit) * rate
            break
    # If the yield_net exceeds the highest limit, tax the remaining income at the highest rate
    highest_limit = tax_rates_items[-1][0]
    if yield_net > highest_limit:
        income_tax += (yield_net - highest_limit) * EXCESS_TAX_RATE
    income_tax = round(round(income_tax, 2) - round(tax_paid, 2), 2)

    kw_report = dict(yield_total=yield_total, tax_paid=tax_paid, to_deduct=to_deduct)
    print(template_render(INCOME_TAX_TEMPLATE, **kw_report, income_tax=income_tax))

    return income_tax


if __name__ == "__main__":
    renta(yield_total=30000, tax_paid=6000, to_deduct=5750)