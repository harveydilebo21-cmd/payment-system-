from datetime import date, timedelta
from decimal import Decimal

from payroll.calculator import calculate_payslip
from payroll.models import AttendanceDay, AttendanceStatus, Employee, Role

PRESENT = AttendanceStatus.PRESENT
UNREGISTERED = AttendanceStatus.UNREGISTERED_ABSENCE
REGISTERED = AttendanceStatus.REGISTERED_ABSENCE


GRASS_CUTTER = Role("Grass Cutter", Decimal("300.00"))
DRIVER = Role("Driver", Decimal("400.00"))

def days(*statuses):
    """Build one attendance record per status, on consecutive dates."""
    start = date(2026, 10, 1)
    return [AttendanceDay(start + timedelta(days=i), s) for i, s in enumerate(statuses)]


def test_full_attendance_is_paid_for_every_day():
    sam = Employee("Sam", GRASS_CUTTER)
    slip = calculate_payslip(sam, days(PRESENT, PRESENT, PRESENT, PRESENT, PRESENT))
    assert slip.net_pay == Decimal("1500.00")

def test_unregistered_absence_is_not_paid():
    sam = Employee("Sam", GRASS_CUTTER)
    slip = calculate_payslip(sam, days(PRESENT, PRESENT, PRESENT, PRESENT, UNREGISTERED))
    assert slip.net_pay == Decimal("1200.00")
    assert slip.deductions == Decimal("300.00")
    assert slip.unpaid_days == 1

def test_registered_absence_is_paid():
    sam = Employee("Sam", GRASS_CUTTER)
    slip = calculate_payslip(sam, days(PRESENT, REGISTERED, PRESENT))
    assert slip.net_pay == Decimal("900.00")
    assert slip.paid_days == 3
    assert slip.unpaid_days == 0


def test_different_roles_earn_different_amounts():
    same_days = days(PRESENT, PRESENT)
    driver = calculate_payslip(Employee("Thabo", DRIVER), same_days)
    cutter = calculate_payslip(Employee("Sam", GRASS_CUTTER), same_days)
    assert driver.net_pay == Decimal("800.00")
    assert cutter.net_pay == Decimal("600.00")


def test_empty_period_pays_zero():
    slip = calculate_payslip(Employee("Sam", GRASS_CUTTER), [])
    assert slip.net_pay == Decimal("0.00")