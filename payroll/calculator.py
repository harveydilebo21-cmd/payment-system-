from payroll.models import AttendanceDay, Employee, Payslip


def calculate_payslip(employee: Employee, attendance: list[AttendanceDay]) -> Payslip:
    paid_days = len(attendance)
    net_pay = employee.role.daily_rate * paid_days
    return Payslip(employee, paid_days, 0, net_pay, 0, net_pay)