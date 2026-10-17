from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class AttendanceStatus(Enum):
    PRESENT = "present"
    REGISTERED_ABSENCE = "registered_absence"
    UNREGISTERED_ABSENCE = "unregistered_absence"


@dataclass(frozen=True)
class Role:
    name: str
    daily_rate: Decimal


@dataclass(frozen=True)
class Employee:
    name: str
    role: Role


@dataclass(frozen=True)
class AttendanceDay:
    date: date
    status: AttendanceStatus

@dataclass(frozen=True)
class Payslip:
    employee: Employee
    paid_days: int
    unpaid_days: int
    potential_pay: Decimal
    deductions: Decimal
    net_pay: Decimal