-- Create a dedicated PostgreSQL role for Odoo (matches .env defaults).
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'odoo') THEN
        CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo' CREATEDB;
    END IF;
END
$$;
