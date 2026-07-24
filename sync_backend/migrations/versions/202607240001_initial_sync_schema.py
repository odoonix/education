from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "202607240001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("odoo_write_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("mobile", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("odoo_id", name="uq_contacts_odoo_id"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("odoo_write_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("internal_reference", sa.String(length=128), nullable=True),
        sa.Column("sale_price", sa.Numeric(16, 4), nullable=False),
        sa.Column("product_type", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("odoo_id", name="uq_products_odoo_id"),
    )
    op.create_table(
        "sale_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("odoo_write_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order_number", sa.String(length=128), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("order_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("total_amount", sa.Numeric(16, 4), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["contacts.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("odoo_id", name="uq_sale_orders_odoo_id"),
    )
    op.create_table(
        "sale_order_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("odoo_write_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sale_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(16, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(16, 4), nullable=False),
        sa.Column("subtotal", sa.Numeric(16, 4), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sale_order_id"], ["sale_orders.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("odoo_id", name="uq_sale_order_lines_odoo_id"),
    )
    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sync_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("inserted_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("unchanged_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lower_watermark", sa.DateTime(timezone=True), nullable=True),
        sa.Column("upper_watermark", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fatal_error", sa.Text(), nullable=True),
    )
    op.create_table(
        "sync_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sync_run_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=True),
        sa.Column("attempted_operation", sa.String(length=64), nullable=False),
        sa.Column("error_type", sa.String(length=128), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["sync_run_id"], ["sync_runs.id"], ondelete="CASCADE"),
    )
    for table in ("contacts", "products", "sale_orders", "sale_order_lines"):
        op.create_index(f"ix_{table}_odoo_write_date", table, ["odoo_write_date"])
    op.create_index("ix_sale_orders_customer_id", "sale_orders", ["customer_id"])
    op.create_index("ix_sale_order_lines_sale_order_id", "sale_order_lines", ["sale_order_id"])
    op.create_index("ix_sale_order_lines_product_id", "sale_order_lines", ["product_id"])
    op.create_index("ix_sync_runs_status_finished", "sync_runs", ["status", "finished_at"])
    op.create_index("ix_sync_logs_sync_run_id", "sync_logs", ["sync_run_id"])


def downgrade() -> None:
    tables: Sequence[str] = (
        "sync_logs",
        "sync_runs",
        "sale_order_lines",
        "sale_orders",
        "products",
        "contacts",
    )
    for table in tables:
        op.drop_table(table)
