from payroll.models import AttendanceDay, AttendanceStatus, Employee, Payslip


def calculate_payslip(employee: Employee, attendance: list[AttendanceDay]) -> Payslip:
    unpaid_days = sum(
        1 for day in attendance if day.status == AttendanceStatus.UNREGISTERED_ABSENCE
    )
    paid_days = len(attendance) - unpaid_days

    rate = employee.role.daily_rate
    net_pay = rate * paid_days
    deductions = rate * unpaid_days
    potential_pay = net_pay + deductions

    return Payslip(employee, paid_days, unpaid_days, potential_pay, deductions, net_pay)