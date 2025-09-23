"""Loan model for book borrowing and returning tracking."""

# pylint: disable=E0611,W0611

from odoo import fields, models


class BooklandLoan(models.Model):
    """Loan model for book borrowing and returning tracking."""

    _name = "bookland.loan"
    _description = "Loan"

    date = fields.Date(string="Loan Date", required=True)
    expire_date = fields.Date()
    note = fields.Text()

    loaner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        domain=[("is_customer", "=", True)],
        required=True,
    )

    book_id = fields.Many2one(
        "bookland.book",
        string="Book",
        required=True,
    )

    state = fields.Selection(
        [
            ("borrowed", "Borrowed"),
            ("returned", "Returned"),
        ],
    )
