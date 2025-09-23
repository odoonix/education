"""Extend res.partner to mark authors and customers."""

# pylint: disable=E0611,W0611


from odoo import fields, models


class BooklandResPartner(models.Model):
    """Extend res.partner to mark authors and customers."""

    _inherit = "res.partner"

    is_author = fields.Boolean(help="Mark partner as author")
    is_customer = fields.Boolean(help="Mark partner as customer")
