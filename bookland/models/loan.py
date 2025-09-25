from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        required=True,
        default="borrowed",
    )

    @api.constrains("expire_date", "date")
    def _check_dates(self):
        for rec in self:
            if rec.expire_date and rec.date and rec.expire_date < rec.date:
                raise ValidationError(_("Expire date cannot be before loan date."))

    @api.model
    def create(self, vals):
        """Override create to handle book quantity."""
        book_id = vals.get("book_id")
        book = self.env["bookland.book"].browse(book_id)
        if vals.get("state") == "borrowed" and book.quantity <= 0:
            raise ValidationError(_("Not enough copies available to loan this book."))
        record = super().create(vals)
        if record.state == "borrowed":
            book = record.book_id.with_context(lock=True)
            if book.quantity <= 0:
                raise ValidationError(
                    _("Not enough copies available to loan this book.")
                )
            book.write({"quantity": book.quantity - 1})
        return record

    def write(self, vals):
        """Override write to handle book quantity changes."""
        for record in self:
            old_state = record.state
            result = super(BooklandLoan, record).write(vals)
            new_state = record.state

            if new_state == "borrowed" and old_state != "borrowed":
                if record.book_id.quantity < 1:
                    raise ValidationError(
                        _("Not enough copies available to loan this book.")
                    )
                else:
                    record.book_id.quantity -= 1

            elif new_state == "returned" and old_state != "returned":
                record.book_id.quantity += 1
        return result
