import sqlite3
from decimal import Decimal

from payroll.models import Employee, Role


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

    def add_role(self, role: Role) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO roles (name, daily_rate) VALUES (?, ?)",
                (role.name, str(role.daily_rate)),
            )

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

    def close(self) -> None:
        self._conn.close()