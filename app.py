import calendar
import sqlite3
from datetime import date
from decimal import Decimal

import streamlit as st
import streamlit.components.v1 as components

from payroll.models import AttendanceStatus, Role
from payroll.payslips import render_payslips_html
from payroll.report import format_money
from payroll.repository import PayrollRepository
from payroll.service import run_payroll

DB_FILE = "payroll.db"

LABELS = {
    "Present": AttendanceStatus.PRESENT,
    "Registered absence (paid)": AttendanceStatus.REGISTERED_ABSENCE,
    "Unregistered absence (unpaid)": AttendanceStatus.UNREGISTERED_ABSENCE,
}
LABEL_OF = {status: label for label, status in LABELS.items()}
NOT_MARKED = "Not marked"

st.set_page_config(page_title="Payroll")
st.title("Payroll")

repo = PayrollRepository(DB_FILE)


def status_on(employee, day):
    for record in repo.get_attendance(employee, day.year, day.month):
        if record.date == day:
            return record.status
    return None


attendance_tab, payslips_tab, setup_tab = st.tabs(
    ["Attendance", "Payslips", "Roles and employees"]
)

# ---------------------------- Attendance ----------------------------
with attendance_tab:
    employees = repo.list_employees()
    if not employees:
        st.info("Add roles and employees first, in the 'Roles and employees' tab.")
    else:
        day = st.date_input("Date", value=date.today())
        options = [NOT_MARKED] + list(LABELS)

        with st.form("attendance_form"):
            choices = {}
            for employee in employees:
                current = status_on(employee, day)
                index = options.index(LABEL_OF[current]) if current else 0
                choices[employee.id] = st.radio(
                    f"{employee.name} ({employee.role.name})",
                    options,
                    index=index,
                    horizontal=True,
                    key=f"attendance-{employee.id}-{day}",
                )
            submitted = st.form_submit_button("Save attendance")

        if submitted:
            for employee in employees:
                choice = choices[employee.id]
                if choice != NOT_MARKED:
                    repo.record_attendance(employee, day, LABELS[choice])
            st.success(f"Attendance saved for {day}.")

# ----------------------------- Payslips -----------------------------
with payslips_tab:
    today = date.today()
    month_names = list(calendar.month_name)[1:]
    left, right = st.columns(2)
    month_name = left.selectbox("Month", month_names, index=today.month - 1)
    year = int(right.number_input("Year", min_value=2020, max_value=2100,
                                  value=today.year, step=1))
    month = month_names.index(month_name) + 1

    pay_run = run_payroll(repo, year, month)

    if not pay_run.payslips:
        st.info("No employees yet.")
    else:
        st.metric("Total cash needed", format_money(pay_run.total_cash))
        st.table([
            {
                "Employee": slip.employee.name,
                "Role": slip.employee.role.name,
                "Days paid": slip.paid_days,
                "Days unpaid": slip.unpaid_days,
                "Net pay": format_money(slip.net_pay),
            }
            for slip in pay_run.payslips
        ])

        page = render_payslips_html(pay_run, year, month)
        st.download_button(
            "Download payslips (open the file, then press Ctrl+P to print)",
            data=page,
            file_name=f"payslips-{year}-{month:02d}.html",
            mime="text/html",
        )
        with st.expander("Preview the payslips"):
            components.html(page, height=700, scrolling=True)

# ------------------------ Roles and employees ------------------------
with setup_tab:
    st.subheader("Add a role")
    with st.form("role_form", clear_on_submit=True):
        role_name = st.text_input("Role name (for example Driver)")
        rate = st.number_input("Daily rate (rand)", min_value=0.0, step=10.0, format="%.2f")
        if st.form_submit_button("Add role"):
            if not role_name.strip() or rate <= 0:
                st.error("Please give the role a name and a rate above zero.")
            else:
                try:
                    repo.add_role(Role(role_name.strip(), Decimal(f"{rate:.2f}")))
                    st.success(f"Added role {role_name.strip()}.")
                except sqlite3.IntegrityError:
                    st.error(f"A role called {role_name.strip()} already exists.")

    roles = repo.list_roles()

    st.subheader("Add an employee")
    if not roles:
        st.info("Add a role first.")
    else:
        with st.form("employee_form", clear_on_submit=True):
            employee_name = st.text_input("Employee name")
            role = st.selectbox("Role", roles, format_func=lambda r: r.name)
            if st.form_submit_button("Add employee"):
                if not employee_name.strip():
                    st.error("Please type the employee's name.")
                else:
                    repo.add_employee(employee_name.strip(), role)
                    st.success(f"Added {employee_name.strip()} as {role.name}.")

    st.subheader("Roles")
    st.table([{"Role": r.name, "Daily rate": format_money(r.daily_rate)}
              for r in repo.list_roles()])

    st.subheader("Employees")
    st.table([{"Name": e.name, "Role": e.role.name,
               "Daily rate": format_money(e.role.daily_rate)}
              for e in repo.list_employees()])

repo.close()
