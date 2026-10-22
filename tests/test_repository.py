from datetime import date
from decimal import Decimal

import pytest

from payroll.models import AttendanceStatus, Role

GRASS_CUTTER = Role("Grass Cutter", Decimal("300.00"))
PRESENT = AttendanceStatus.PRESENT
UNREGISTERED = AttendanceStatus.UNREGISTERED_ABSENCE


def test_saved_employee_can_be_read_back(repo):
    repo.add_role(GRASS_CUTTER)
    saved = repo.add_employee("Sam", GRASS_CUTTER)

    assert saved.id is not None
    assert repo.list_employees() == [saved]


def test_daily_rate_survives_storage_exactly(repo):
    driver = Role("Driver", Decimal("412.35"))
    repo.add_role(driver)
    repo.add_employee("Thabo", driver)

    assert repo.list_employees()[0].role.daily_rate == Decimal("412.35")

def test_recorded_attendance_can_be_read_back(repo):
    repo.add_role(GRASS_CUTTER)
    sam = repo.add_employee("Sam", GRASS_CUTTER)

    repo.record_attendance(sam, date(2026, 10, 1), PRESENT)

    records = repo.get_attendance(sam, 2026, 10)
    assert [(r.date, r.status) for r in records] == [(date(2026, 10, 1), PRESENT)]


def test_recording_the_same_day_again_corrects_it(repo):
    repo.add_role(GRASS_CUTTER)
    sam = repo.add_employee("Sam", GRASS_CUTTER)

    repo.record_attendance(sam, date(2026, 10, 1), PRESENT)
    repo.record_attendance(sam, date(2026, 10, 1), UNREGISTERED)   # fixing a mistake

    records = repo.get_attendance(sam, 2026, 10)
    assert len(records) == 1
    assert records[0].status == UNREGISTERED


def test_attendance_is_filtered_by_month_and_sorted(repo):
    repo.add_role(GRASS_CUTTER)
    sam = repo.add_employee("Sam", GRASS_CUTTER)

    repo.record_attendance(sam, date(2026, 10, 15), PRESENT)
    repo.record_attendance(sam, date(2026, 9, 30), PRESENT)    # previous month
    repo.record_attendance(sam, date(2026, 11, 1), PRESENT)    # next month
    repo.record_attendance(sam, date(2026, 10, 2), PRESENT)

    dates = [r.date for r in repo.get_attendance(sam, 2026, 10)]
    assert dates == [date(2026, 10, 2), date(2026, 10, 15)]


def test_attendance_for_an_unsaved_employee_is_rejected(repo):
    from payroll.models import Employee
    unsaved = Employee("Ghost", GRASS_CUTTER)   # no id, never stored
    with pytest.raises(ValueError):
        repo.record_attendance(unsaved, date(2026, 10, 1), PRESENT)

def test_roles_can_be_listed_alphabetically(repo):
    repo.add_role(GRASS_CUTTER)
    repo.add_role(Role("Driver", Decimal("400.00")))

    assert repo.list_roles() == [Role("Driver", Decimal("400.00")), GRASS_CUTTER]
    