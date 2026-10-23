from datetime import date, timedelta
from decimal import Decimal

from payroll.calculator import calculate_pay_run
from payroll.models import AttendanceDay, AttendanceStatus, Employee, Role
from payroll.payslips import render_payslips_html, save_payslips_html

PRESENT = AttendanceStatus.PRESENT
UNREGISTERED = AttendanceStatus.UNREGISTERED_ABSENCE

DRIVER = Role("Driver", Decimal("400.00"))
GRASS_CUTTER = Role("Grass Cutter", Decimal("300.00"))


def days(*statuses):
    start = date(2026, 10, 1)
    return [AttendanceDay(start + timedelta(days=i), s) for i, s in enumerate(statuses)]


def make_pay_run():
    return calculate_pay_run({
        Employee("Thabo", DRIVER): days(PRESENT, PRESENT),                  # 800
        Employee("Sam", GRASS_CUTTER): days(PRESENT, PRESENT, UNREGISTERED),  # 600
    })


def test_there_is_one_payslip_page_per_employee():
    page = render_payslips_html(make_pay_run(), 2026, 10)
    assert page.count('class="payslip"') == 2


def test_amounts_and_total_cash_are_shown():
    page = render_payslips_html(make_pay_run(), 2026, 10)
    assert "R800.00" in page      
    assert "R600.00" in page      
    assert "R300.00" in page      
    assert "TOTAL CASH NEEDED" in page
    assert "R1,400.00" in page
    assert "October 2026" in page


def test_each_payslip_has_a_signature_line_for_cash_payment():
    page = render_payslips_html(make_pay_run(), 2026, 10)
    assert page.count("Received in cash") == 2


def test_names_are_escaped_so_they_cannot_break_the_page():
    pay_run = calculate_pay_run({Employee("<b>Sam</b>", GRASS_CUTTER): days(PRESENT)})
    page = render_payslips_html(pay_run, 2026, 10)
    assert "<b>Sam</b>" not in page
    assert "&lt;b&gt;Sam&lt;/b&gt;" in page


def test_payslips_can_be_saved_to_a_file(tmp_path):
    path = save_payslips_html(make_pay_run(), 2026, 10, tmp_path / "payslips")

    assert path.name == "payslips-2026-10.html"
    assert path.exists()
    assert "Thabo" in path.read_text(encoding="utf-8")