![Tests](https://github.com/harveydilebo21-cmd/payment-system-/actions/workflows/tests.yml/badge.svg)

My Aunt ran a small company focused on forest clearing, employees have daily rates but they all rate differently according to what they do
for example the driver does not have the same daily rate as the grass cutter, so she was always trapped under a mountain of paperwork and stuck with a calculator trying to calculate how much each employee is owed and deducting if the employee has unregistered absences.
So I decided to create A streamlined, role-based workforce management and automated wage calculation platform engineered to eliminate manual bookkeeping, track attendance anomalies, and automate variable-tier payroll for field-service operations.

Small-to-medium field-service businesses—such as vegetation management, forestry, and land clearing—operate under highly dynamic labor structures:

Tiered Variable Wage Rates: Workers receive different daily base rates depending on their operational duties (e.g., Heavy Vehicle Drivers, Chainsaw Operators, Brush Cutters, General Laborers).

Manual Bookkeeping Bottlenecks: Tracking shifts, overtime, and irregular work schedules with physical paper logs leads to calculation errors and administrative strain.

Attendance & Absence Penalties: Unregistered absences, unverified sick days, and partial shifts require accurate prorated deductions rather than manual guesswork.

The Solution: An automated payroll engine that manages employee registries, captures day-by-day attendance logs, computes net wages based on assigned labor classifications, and exports audit-ready payout sheets.

✨ Core Features & Functional Capabilities

1. 👥 Dynamic Role & Rate Registry

Configurable labor tiers with distinct daily base rates (e.g., Driver, Machine Operator, Cutter, Field Assistant).

Historical wage tracking: Adjust rates without corrupting prior payroll cycles.

2. 📅 Shift & Attendance Accounting

Rapid daily roster verification (Present, Excused Absence, Unregistered Absence, Half-Day).

Automated penalty calculations: flags and calculates prorated deductions for unexcused no-shows.

3. 🧮 Automated Calculation Engine

$$\text{Net Payout} = (\text{Days Worked} \times \text{Daily Rate}) + \text{Overtime/Bonuses} - \text{Absence Deductions}$$

Prevents rounding errors and ensures accurate accounting down to the cent.

Supports pay period customization (Weekly, Bi-weekly, or Monthly reconciliations).

4. 📊 Reporting & Payout Breakdown

Generates clean, itemized wage summaries per worker.

Export options for CSV and formatted PDF payslips.

Executive summary displaying total operational labor cost for each clearing site.

🛠️ Technical Stack & Architecture

Layer

Technology

Purpose

Backend & Logic

Python (FastAPI / Flask)

Core calculation engine, business rules, and RESTful API endpoints.

Database & ORM

PostgreSQL / SQLite + SQLAlchemy

Relational data schema tracking roles, attendance logs, and transactional records.

Containerization

Docker & Docker Compose

Reproducible local development and lightweight zero-dependency deployment.

Testing & CI

PyTest + GitHub Actions

TDD approach covering edge-case calculations, leap days, and missing logs.

Frontend / UI

HTML / Tailwind CSS / Vanilla JS (or CLI tool)

Intuitive dashboard allowing rapid batch-marking of employee attendance.

🏗️ System Architecture & Data Schema

[ Field Operations / Attendance Logs ]
                 │
                 ▼
     [ API / Validation Layer ]
                 │
  ┌──────────────┴──────────────┐
  ▼                             ▼
[ Employee / Role Schema ]   [ Payroll Computation Engine ]
  • Worker ID                  • Shift Aggregator
  • Assigned Job Class         • Proration & Penalty Rules
  • Base Daily Rate            • Net Wage Derivation
  └──────────────┬──────────────┘
                 │
                 ▼
       [ PostgreSQL Database ]
                 │
                 ▼
   [ Automated Report / PDF Payslip ]



Test cases cover:

Variable daily wage calculations across multiple role categories.

Prorated shift calculations for split attendance.

Complete absence penalty deduction accuracy.


👨‍💻 Author & Contact

Developed by Keabetswe Harvey Dilebo

GitHub: @harveydilebo21-cmd

LinkedIn: Keabetswe Harvey Dilebo

Email: harveydilebo21@gmail.com
