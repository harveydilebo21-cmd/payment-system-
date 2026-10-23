import calendar
import html
from pathlib import Path

from payroll.models import PayRun, Payslip
from payroll.report import format_money

_STYLE = """
body { font-family: Arial, sans-serif; color: #222; }
.payslip, .summary { max-width: 600px; margin: 0 auto 40px; padding: 24px; border: 1px solid #999; }
h1 { font-size: 1.3em; margin-top: 0; }
h2 { margin-bottom: 0; }
table { width: 100%; border-collapse: collapse; margin-top: 16px; }
td { padding: 6px 0; border-bottom: 1px solid #ddd; }
td.amount { text-align: right; }
tr.net td { font-weight: bold; font-size: 1.15em; border-bottom: 2px solid #222; }
.signature { margin-top: 56px; }
@media print {
  .payslip { page-break-after: always; border: none; }
  .summary { border: none; }
}
"""


def _row(label: str, value: object, css_class: str = "") -> str:
    return f'<tr class="{css_class}"><td>{label}</td><td class="amount">{value}</td></tr>'


def _payslip_section(slip: Payslip, period: str) -> str:
    name = html.escape(slip.employee.name)
    role = html.escape(slip.employee.role.name)
    rows = [
        _row("Daily rate", format_money(slip.employee.role.daily_rate)),
        _row("Days paid", slip.paid_days),
        _row("Days unpaid (unregistered absence)", slip.unpaid_days),
        _row("Pay before deductions", format_money(slip.potential_pay)),
        _row("Deductions", format_money(slip.deductions)),
        _row("NET PAY", format_money(slip.net_pay), "net"),
    ]
    return (
        '<section class="payslip">'
        f"<h1>Payslip - {period}</h1>"
        f"<h2>{name}</h2><p>{role}</p>"
        f"<table>{''.join(rows)}</table>"
        '<p class="signature">Received in cash: ____________________ '
        "&nbsp;&nbsp; Date: ______________</p>"
        "</section>"
    )


def _summary_section(pay_run: PayRun, period: str) -> str:
    rows = "".join(
        _row(
            f"{html.escape(s.employee.name)} ({html.escape(s.employee.role.name)})",
            format_money(s.net_pay),
        )
        for s in pay_run.payslips
    )
    total = _row("TOTAL CASH NEEDED", format_money(pay_run.total_cash), "net")
    return (
        '<section class="summary">'
        f"<h1>Pay run summary - {period}</h1>"
        f"<table>{rows}{total}</table>"
        "</section>"
    )


def render_payslips_html(pay_run: PayRun, year: int, month: int) -> str:
    period = f"{calendar.month_name[month]} {year}"
    sections = [_payslip_section(slip, period) for slip in pay_run.payslips]
    sections.append(_summary_section(pay_run, period))
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        f"<title>Payslips {period}</title><style>{_STYLE}</style></head>"
        f"<body>{''.join(sections)}</body></html>"
    )


def save_payslips_html(pay_run: PayRun, year: int, month: int, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"payslips-{year}-{month:02d}.html"
    path.write_text(render_payslips_html(pay_run, year, month), encoding="utf-8")
    return path