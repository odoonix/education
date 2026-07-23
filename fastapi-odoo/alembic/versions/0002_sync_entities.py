"""create sync entities from odoo

Revision ID: 0002_sync_entities
Revises: 0001_create_items
Create Date: 2026-07-23 13:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_sync_entities"
down_revision: Union[str, None] = "0001_create_items"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("street", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("is_company", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
    )
    op.create_index(op.f("ix_contacts_id"), "contacts", ["id"], unique=False)
    op.create_index(op.f("ix_contacts_odoo_id"), "contacts", ["odoo_id"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("default_code", sa.String(length=64), nullable=True),
        sa.Column("list_price", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column("uom_name", sa.String(length=64), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
    )
    op.create_index(op.f("ix_products_default_code"), "products", ["default_code"], unique=False)
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_odoo_id"), "products", ["odoo_id"], unique=True)

    op.create_table(
        "sale_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("amount_total", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column("date_order", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
    )
    op.create_index(op.f("ix_sale_orders_contact_id"), "sale_orders", ["contact_id"], unique=False)
    op.create_index(op.f("ix_sale_orders_id"), "sale_orders", ["id"], unique=False)
    op.create_index(op.f("ix_sale_orders_name"), "sale_orders", ["name"], unique=False)
    op.create_index(op.f("ix_sale_orders_odoo_id"), "sale_orders", ["odoo_id"], unique=True)

    op.create_table(
        "sale_order_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("odoo_id", sa.Integer(), nullable=False),
        sa.Column("sale_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("product_uom_qty", sa.Numeric(precision=16, scale=4), nullable=False, server_default="0"),
        sa.Column("price_unit", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column("price_subtotal", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["sale_order_id"], ["sale_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("odoo_id"),
    )
    op.create_index(op.f("ix_sale_order_lines_id"), "sale_order_lines", ["id"], unique=False)
    op.create_index(op.f("ix_sale_order_lines_odoo_id"), "sale_order_lines", ["odoo_id"], unique=True)
    op.create_index(op.f("ix_sale_order_lines_product_id"), "sale_order_lines", ["product_id"], unique=False)
    op.create_index(op.f("ix_sale_order_lines_sale_order_id"), "sale_order_lines", ["sale_order_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sale_order_lines_sale_order_id"), table_name="sale_order_lines")
    op.drop_index(op.f("ix_sale_order_lines_product_id"), table_name="sale_order_lines")
    op.drop_index(op.f("ix_sale_order_lines_odoo_id"), table_name="sale_order_lines")
    op.drop_index(op.f("ix_sale_order_lines_id"), table_name="sale_order_lines")
    op.drop_table("sale_order_lines")

    op.drop_index(op.f("ix_sale_orders_odoo_id"), table_name="sale_orders")
    op.drop_index(op.f("ix_sale_orders_name"), table_name="sale_orders")
    op.drop_index(op.f("ix_sale_orders_id"), table_name="sale_orders")
    op.drop_index(op.f("ix_sale_orders_contact_id"), table_name="sale_orders")
    op.drop_table("sale_orders")

    op.drop_index(op.f("ix_products_odoo_id"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_index(op.f("ix_products_default_code"), table_name="products")
    op.drop_table("products")

    op.drop_index(op.f("ix_contacts_odoo_id"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_id"), table_name="contacts")
    op.drop_table("contacts")
