import pytest

from payroll.repository import PayrollRepository


@pytest.fixture
def repo():
    repository = PayrollRepository()   # no path = temporary in-memory database
    yield repository
    repository.close()