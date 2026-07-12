# Billing & GST Management System — Backend

Flask REST API for a GST billing system: dealers, deals, items, and bill
generation (dealer and farmer bills) with interest calculations, PDF invoices,
and Excel export. Serves the
[Billing-GST-Management-System](https://github.com/123yogin/Billing-GST-Management-System) frontend.

## Features

- **Dealers, deals, and items** management (CRUD)
- **Billing** for both dealer and farmer bills, with GST/invoice fields
- **Interest calculations** and billing math (`utils/calculations.py`, `interest_calculations.py`)
- **PDF invoice generation** (xhtml2pdf) and **Excel export** (pandas / openpyxl)
- **Reports** endpoints
- Versioned schema via Alembic (Flask-Migrate)

## Tech stack

- Python + Flask (Blueprints)
- PostgreSQL (SQLAlchemy + Flask-Migrate, psycopg2)
- xhtml2pdf, pandas, openpyxl, Flask-CORS

## Getting started

```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
# set DATABASE_URL / config (see config.py), then:
flask db upgrade          # apply migrations
python run.py
```

## Project structure

```
app/
├─ dealers/  deals/  items/  billing/  reports/    feature blueprints (routes)
├─ models.py
└─ utils/    calculations.py, interest_calculations.py, pdf_generator.py
migrations/  Alembic migration history
run.py
```
