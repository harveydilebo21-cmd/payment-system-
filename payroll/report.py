import calendar
from decimal import Decimal

from payroll.models import PayRun, Payslip


def format_money(amount: Decimal) -> str:
    return f"R{amount:,.2f}"


def format_payslip(slip: Payslip) -> str:
    rate = slip.employee.role.daily_rate
    return "\n".join([
        f"{slip.employee.name} ({slip.employee.role.name})",
        f"  Daily rate:   {format_money(rate)}",
        f"  Days paid:    {slip.paid_days}",
        f"  Days unpaid:  {slip.unpaid_days}",
        f"  Deductions:   {format_money(slip.deductions)}",
        f"  NET PAY:      {format_money(slip.net_pay)}",
    ])


def format_pay_run(pay_run: PayRun, year: int, month: int) -> str:
    divider = "-" * 40
    lines = [f"PAYROLL - {calendar.month_name[month]} {year}", divider]
    for slip in pay_run.payslips:
        lines.append(format_payslip(slip))
        lines.append(divider)
    lines.append(f"TOTAL CASH NEEDED: {format_money(pay_run.total_cash)}")
    return "\n".join(lines)