import sqlite3
from datetime import date
from decimal import Decimal

from payroll.models import AttendanceDay, AttendanceStatus, Employee, Role


class PayrollRepository:
    def __init__(self, path: str = ":memory:"):
        self._conn = sqlite3.connect(path)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self) -> None:
        with self._conn:
            self._conn.execute(
                """CREATE TABLE IF NOT EXISTS roles (
                       name TEXT PRIMARY KEY,
                       daily_rate TEXT NOT NULL
                   )"""
            )
            self._conn.execute(
                """CREATE TABLE IF NOT EXISTS employees (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       role_name TEXT NOT NULL REFERENCES roles(name)
                   )"""
            )
            self._conn.execute(
                """CREATE TABLE IF NOT EXISTS attendance (
                       employee_id INTEGER NOT NULL REFERENCES employees(id),
                       day TEXT NOT NULL,
                       status TEXT NOT NULL,
                       PRIMARY KEY (employee_id, day)
                   )"""
            )

    def add_role(self, role: Role) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO roles (name, daily_rate) VALUES (?, ?)",
                (role.name, str(role.daily_rate)),
            )

    def list_roles(self) -> list[Role]:
        rows = self._conn.execute(
            "SELECT name, daily_rate FROM roles ORDER BY name"
        ).fetchall()
        return [Role(name, Decimal(rate)) for name, rate in rows]
        

    def add_employee(self, name: str, role: Role) -> Employee:
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO employees (name, role_name) VALUES (?, ?)",
                (name, role.name),
            )
        return Employee(name, role, cursor.lastrowid)

    def list_employees(self) -> list[Employee]:
        rows = self._conn.execute(
            """SELECT e.id, e.name, r.name, r.daily_rate
               FROM employees e
               JOIN roles r ON r.name = e.role_name
               ORDER BY e.name"""
        ).fetchall()
        return [
            Employee(name, Role(role_name, Decimal(rate)), emp_id)
            for emp_id, name, role_name, rate in rows
        ]

    def record_attendance(
        self, employee: Employee, day: date, status: AttendanceStatus
    ) -> None:
        if employee.id is None:
            raise ValueError("Employee has not been saved yet")
        with self._conn:
            self._conn.execute(
                """INSERT INTO attendance (employee_id, day, status)
                   VALUES (?, ?, ?)
                   ON CONFLICT(employee_id, day)
                   DO UPDATE SET status = excluded.status""",
                (employee.id, day.isoformat(), status.value),
            )

    def get_attendance(
        self, employee: Employee, year: int, month: int
    ) -> list[AttendanceDay]:
        start = date(year, month, 1)
        end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        rows = self._conn.execute(
            """SELECT day, status FROM attendance
               WHERE employee_id = ? AND day >= ? AND day < ?
               ORDER BY day""",
            (employee.id, start.isoformat(), end.isoformat()),
        ).fetchall()
        return [
            AttendanceDay(date.fromisoformat(day), AttendanceStatus(status))
            for day, status in rows
        ]

    def close(self) -> None:
        self._conn.close()