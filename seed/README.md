# Odoo Seed Script

## Overview

This directory contains a simple Python script used to populate the Odoo instance with sample data required for the technical assessment.

The script inserts:

* Contacts
* Products
* Sale Orders
* Sale Order Lines

The data is loaded from JSON files and sent to Odoo using the XML-RPC API.

---

## Requirements

Before running the script:

* Odoo must be running.
* The target database must already exist.
* The required Odoo applications (Contacts, Sales, Products) must be installed.
* An administrator account must be available.

---

## Configuration

The script reads its configuration from the project's root `.env` file using **Pydantic Settings**.

Example:

```env
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_ADMIN_EMAIL=admin
ODOO_ADMIN_PASSWORD=admin
```

---

## Data Files

Sample data is stored inside the `data/` directory.

```
seed/
├── data/
│   ├── contacts.json
│   ├── products.json
│   └── sale_orders.json
```

These files can be modified to generate different datasets.

---

## Running

The project uses **uv** as the Python package manager.

Execute the seeder from the project root:

```bash
uv run python seed/seed.py
```

---

## Implementation Notes

* XML-RPC is used to communicate with Odoo.
* Configuration is managed with Pydantic Settings.
* JSON files are used to keep the sample data separate from the implementation.
* The script is intentionally simple because its only responsibility is generating test data for the backend synchronization service.

It is **not** intended to be a production-grade data import tool.

---

## Purpose

The purpose of this script is solely to prepare a repeatable Odoo environment for testing the backend synchronization system implemented in this technical assessment.
