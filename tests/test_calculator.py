from datetime import date, timedelta
from decimal import Decimal

from payroll.calculator import calculate_payslip
from payroll.models import AttendanceDay, AttendanceStatus, Employee, Role

PRESENT = AttendanceStatus.PRESENT
UNREGISTERED = AttendanceStatus.UNREGISTERED_ABSENCE

GRASS_CUTTER = Role("Grass Cutter", Decimal("300.00"))


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