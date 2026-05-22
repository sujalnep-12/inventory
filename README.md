# Fynnet Inventory Management System

Local Django inventory system for Fynnet Computer and Digital Services.

## Features

- Product stock, cost price, selling price, low-stock alerts, and stock value
- Service catalog with standard price and delivery cost
- Sales invoices with product and service line items
- Automatic stock reduction for sold products
- Daily sales, expenses, gross profit, net profit, cash received, and remaining balance
- Expense tracking
- Stock adjustments for restock, removal, and corrections
- Date-range reports
- Excel export as `.xlsx`

## Run Locally

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/`.

The local SQLite database is stored at `db.sqlite3` in this project folder.

## Admin User

Create an admin user when needed:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Then open `http://127.0.0.1:8000/admin/`.
