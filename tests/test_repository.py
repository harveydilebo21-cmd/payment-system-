from decimal import Decimal

import pytest

from payroll.models import Role
from payroll.repository import PayrollRepository

GRASS_CUTTER = Role("Grass Cutter", Decimal("300.00"))


@pytest.fixture
def repo():
    repository = PayrollRepository()   # no path given = temporary in-memory database
    yield repository
    repository.close()


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