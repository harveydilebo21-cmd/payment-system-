from decimal import Decimal

from payroll.models import AttendanceDay, AttendanceStatus, Employee, PayRun, Payslip

def calculate_payslip(employee: Employee, attendance: list[AttendanceDay]) -> Payslip:
    _reject_duplicate_dates(attendance)

    unpaid_days = sum(
        1 for day in attendance if day.status == AttendanceStatus.UNREGISTERED_ABSENCE
    )
    paid_days = len(attendance) - unpaid_days   # present + registered absences

    rate = employee.role.daily_rate
    net_pay = rate * paid_days
    deductions = rate * unpaid_days
    potential_pay = net_pay + deductions

    return Payslip(employee, paid_days, unpaid_days, potential_pay, deductions, net_pay)


def _reject_duplicate_dates(attendance: list[AttendanceDay]) -> None:
    seen = set()
    for day in attendance:
        if day.date in seen:
            raise ValueError(f"Duplicate attendance for {day.date}")
        seen.add(day.date)


def calculate_pay_run(
    attendance_by_employee: dict[Employee, list[AttendanceDay]],
) -> PayRun:
    payslips = tuple(
        calculate_payslip(employee, attendance)
        for employee, attendance in attendance_by_employee.items()
    )
    total_cash = sum((slip.net_pay for slip in payslips), Decimal("0.00"))
    return PayRun(payslips, total_cash)