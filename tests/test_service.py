from datetime import date
from decimal import Decimal

from payroll.models import AttendanceStatus, Role
from payroll.service import run_payroll

PRESENT = AttendanceStatus.PRESENT
UNREGISTERED = AttendanceStatus.UNREGISTERED_ABSENCE

DRIVER = Role("Driver", Decimal("400.00"))
GRASS_CUTTER = Role("Grass Cutter", Decimal("300.00"))


def test_payroll_is_calculated_from_stored_attendance(repo):
    repo.add_role(DRIVER)
    repo.add_role(GRASS_CUTTER)
    thabo = repo.add_employee("Thabo", DRIVER)
    sam = repo.add_employee("Sam", GRASS_CUTTER)

    repo.record_attendance(thabo, date(2026, 10, 1), PRESENT)       # 400
    repo.record_attendance(thabo, date(2026, 10, 2), PRESENT)       # 400
    repo.record_attendance(sam, date(2026, 10, 1), PRESENT)         # 300
    repo.record_attendance(sam, date(2026, 10, 2), UNREGISTERED)    # 0
    repo.record_attendance(sam, date(2026, 11, 1), PRESENT)         # other month, ignored

    pay_run = run_payroll(repo, 2026, 10)

    assert pay_run.total_cash == Decimal("1100.00")
    assert len(pay_run.payslips) == 2