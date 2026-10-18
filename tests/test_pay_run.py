from datetime import date, timedelta
from decimal import Decimal

from payroll.calculator import calculate_pay_run
from payroll.models import AttendanceDay, AttendanceStatus, Employee, Role

PRESENT = AttendanceStatus.PRESENT
UNREGISTERED = AttendanceStatus.UNREGISTERED_ABSENCE

DRIVER = Role("Driver", Decimal("400.00"))
GRASS_CUTTER = Role("Grass Cutter", Decimal("300.00"))


def days(*statuses):
    start = date(2026, 10, 1)
    return [AttendanceDay(start + timedelta(days=i), s) for i, s in enumerate(statuses)]


def test_total_cash_is_the_sum_of_everyones_net_pay():
    thabo = Employee("Thabo", DRIVER)
    sam = Employee("Sam", GRASS_CUTTER)

    pay_run = calculate_pay_run({
        thabo: days(PRESENT, PRESENT),                 # 2 x 400 = 800
        sam: days(PRESENT, PRESENT, UNREGISTERED),     # 2 x 300 = 600
    })

    assert pay_run.total_cash == Decimal("1400.00")

def test_pay_run_has_one_payslip_per_employee():
    thabo = Employee("Thabo", DRIVER)
    sam = Employee("Sam", GRASS_CUTTER)

    pay_run = calculate_pay_run({thabo: days(PRESENT), sam: days(PRESENT)})

    assert len(pay_run.payslips) == 2


def test_empty_pay_run_totals_zero():
    pay_run = calculate_pay_run({})
    assert pay_run.total_cash == Decimal("0.00")
    assert pay_run.payslips == ()