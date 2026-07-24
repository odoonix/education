# Odoo → PostgreSQL Sync Backend

This is my solution for the technical exam. It pulls contacts, products, and sale orders out of Odoo and stores them in my own PostgreSQL database, without creating duplicates if you run it more than once.

## What's in here

- An Odoo instance running in Docker (I set this up myself, no server was given to me for the exam)
- A small script to create some test data in Odoo (contacts, products, sale orders)
- A Python backend that connects to Odoo, pulls the data, and saves it to Postgres
- Tests for the important parts
- Docs: `USER.md` (how to run everything) and `TECHNICAL.md` (how it's built and why)

## Quick start

```powershell
docker compose up -d odoo-db odoo app-db
```

Then open `http://localhost:8069`, log in / create the database, install the Sales app, and run the seed script. Full steps are in `USER.md`.

## Why it's built this way

I split the code into layers: one part just talks to Odoo, one part maps Odoo's data into my own format, one part handles saving to the database, and one part ties it all together and keeps track of what happened (what got created, what got updated, what failed). This way if I ever needed to swap Odoo for a different system, or Postgres for something else, I wouldn't have to rewrite everything — just the one piece that changed.

## Status

Still learning parts of this as I go — some of the design decisions I made because they're generally good practice, and I'll be able to explain them properly once I've had time to sit with the whole project and understand it end to end.
