from datetime import date
from decimal import Decimal, InvalidOperation
import sqlite3

from payroll.models import AttendanceStatus, Role
from payroll.report import format_money, format_pay_run
from payroll.repository import PayrollRepository
from payroll.service import run_payroll

DB_FILE = "payroll.db"

STATUS_KEYS = {
    "p": AttendanceStatus.PRESENT,
    "r": AttendanceStatus.REGISTERED_ABSENCE,
    "u": AttendanceStatus.UNREGISTERED_ABSENCE,
}


# ---------- small input helpers: keep asking until the answer is valid ----------

def ask_text(prompt: str) -> str:
    while True:
        answer = input(prompt).strip()
        if answer:
            return answer
        print("Please type something.")


def ask_money(prompt: str) -> Decimal:
    while True:
        try:
            amount = Decimal(input(prompt).strip())
            if amount > 0:
                return amount.quantize(Decimal("0.01"))
        except InvalidOperation:
            pass
        print("Please type an amount like 350 or 412.50.")


def ask_date(prompt: str) -> date:
    while True:
        answer = input(prompt).strip()
        if not answer:
            return date.today()
        try:
            return date.fromisoformat(answer)
        except ValueError:
            print("Please use the format YYYY-MM-DD, for example 2026-10-22.")


def ask_month(prompt: str) -> tuple[int, int]:
    while True:
        answer = input(prompt).strip()
        if not answer:
            today = date.today()
            return today.year, today.month
        try:
            year_text, month_text = answer.split("-")
            year, month = int(year_text), int(month_text)
            date(year, month, 1)   # raises ValueError if the month is invalid
            return year, month
        except ValueError:
            print("Please use the format YYYY-MM, for example 2026-10.")


def ask_choice(prompt: str, count: int) -> int:
    while True:
        answer = input(prompt).strip()
        if answer.isdigit() and 1 <= int(answer) <= count:
            return int(answer) - 1
        print(f"Please type a number from 1 to {count}.")


# ---------- menu actions ----------

def add_role(repo: PayrollRepository) -> None:
    name = ask_text("Role name (e.g. Driver): ")
    rate = ask_money("Daily rate in rand: ")
    try:
        repo.add_role(Role(name, rate))
        print(f"Added role {name} at {format_money(rate)} per day.")
    except sqlite3.IntegrityError:
        print(f"A role called {name} already exists.")


def add_employee(repo: PayrollRepository) -> None:
    roles = repo.list_roles()
    if not roles:
        print("Add a role first (option 1).")
        return
    name = ask_text("Employee name: ")
    for number, role in enumerate(roles, start=1):
        print(f"  {number}. {role.name} ({format_money(role.daily_rate)} per day)")
    role = roles[ask_choice("Choose a role number: ", len(roles))]
    repo.add_employee(name, role)
    print(f"Added {name} as {role.name}.")


def current_status(repo, employee, day):
    for record in repo.get_attendance(employee, day.year, day.month):
        if record.date == day:
            return record.status
    return None


def mark_attendance(repo: PayrollRepository) -> None:
    employees = repo.list_employees()
    if not employees:
        print("Add an employee first (option 2).")
        return
    day = ask_date("Date (YYYY-MM-DD, or press Enter for today): ")
    print(f"Attendance for {day}")
    print("  p = present, r = registered absence, u = unregistered absence")
    print("  Enter = skip this person")
    for employee in employees:
        existing = current_status(repo, employee, day)
        hint = f" [now: {existing.value}]" if existing else ""
        while True:
            key = input(f"  {employee.name} ({employee.role.name}){hint}: ").strip().lower()
            if key == "":
                break
            if key in STATUS_KEYS:
                repo.record_attendance(employee, day, STATUS_KEYS[key])
                break
            print("  Please type p, r, u, or press Enter to skip.")


def show_payroll(repo: PayrollRepository) -> None:
    year, month = ask_month("Month (YYYY-MM, or press Enter for this month): ")
    pay_run = run_payroll(repo, year, month)
    print()
    print(format_pay_run(pay_run, year, month))


# ---------- main menu ----------

MENU = """
=== Payroll ===
1. Add a role (e.g. Driver, Grass Cutter)
2. Add an employee
3. Mark attendance for a day
4. Show payslips for a month
5. Quit
"""

ACTIONS = {"1": add_role, "2": add_employee, "3": mark_attendance, "4": show_payroll}


def main() -> None:
    repo = PayrollRepository(DB_FILE)
    try:
        while True:
            print(MENU)
            choice = input("Choose 1-5: ").strip()
            if choice == "5":
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("Please choose a number from 1 to 5.")
            else:
                action(repo)
    finally:
        repo.close()
    print("Goodbye.")


if __name__ == "__main__":
    main()