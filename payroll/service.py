from payroll.calculator import calculate_pay_run
from payroll.models import PayRun
from payroll.repository import PayrollRepository


def run_payroll(repo: PayrollRepository, year: int, month: int) -> PayRun:
    attendance_by_employee = {
        employee: repo.get_attendance(employee, year, month)
        for employee in repo.list_employees()
    }
    return calculate_pay_run(attendance_by_employee)

