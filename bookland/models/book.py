"""Book model representing a library book with price, quantity, authors."""

# pylint: disable=E0611,W0611


from odoo import fields, models, api
from odoo.exceptions import UserError


class BooklandBook(models.Model):
    """Book model representing a library book with price, quantity, authors."""

    _name = "bookland.book"
    _description = "Book"

    name = fields.Char(
        string="Book Title",
        help="Store the title of the book",
        translate=True,
        required=True,
        index=True,
        size=512,
    )
    description = fields.Html(
        required=False,
        translate=True,
        index=False,
    )
    publish_date = fields.Date()
    isbn = fields.Char(size=13)

    price = fields.Monetary(
        string="Book Price",
        required=True,
        help="""
<h1>Price of the Book</h1>
<p>How much the book should sell on store</p>
""",
    )

    quantity = fields.Integer(string="Available Quantity", default=1)

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
    )
    language_id = fields.Many2one("res.lang")

    author_ids = fields.Many2many(
        "res.partner",
        string="Authors",
        domain=[("is_author", "=", True)],
        required=True,
    )

    def action_open_loan_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Loan",
            "res_model": "bookland.loan",
            "view_mode": "form",
            "view_id": self.env.ref("bookland.loan_form_view").id,
            "target": "new",
            "context": {
                "default_book_id": self.id,
                "default_date": fields.Date.today(),
            },
        }
