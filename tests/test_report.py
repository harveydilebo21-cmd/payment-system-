from datetime import date, timedelta
from decimal import Decimal

from payroll.calculator import calculate_pay_run, calculate_payslip
from payroll.models import AttendanceDay, AttendanceStatus, Employee, Role
from payroll.report import format_money, format_pay_run, format_payslip

PRESENT = AttendanceStatus.PRESENT
UNREGISTERED = AttendanceStatus.UNREGISTERED_ABSENCE

SAM = Employee("Sam", Role("Grass Cutter", Decimal("300.00")))


def days(*statuses):
    start = date(2026, 10, 1)
    return [AttendanceDay(start + timedelta(days=i), s) for i, s in enumerate(statuses)]


def test_money_is_shown_in_rand_with_two_decimals():
    assert format_money(Decimal("1500")) == "R1,500.00"
    assert format_money(Decimal("0")) == "R0.00"


def test_payslip_shows_who_what_and_how_much():
    slip = calculate_payslip(SAM, days(PRESENT, PRESENT, PRESENT, PRESENT, UNREGISTERED))
    text = format_payslip(slip)

    assert "Sam" in text
    assert "Grass Cutter" in text
    assert "R1,200.00" in text   # net pay
    assert "R300.00" in text     # the deduction (and the daily rate)


def test_pay_run_report_shows_month_and_total_cash():
    pay_run = calculate_pay_run({SAM: days(PRESENT, PRESENT, UNREGISTERED)})
    text = format_pay_run(pay_run, 2026, 10)

    assert "October 2026" in text
    assert "TOTAL CASH" in text
    assert "R600.00" in text