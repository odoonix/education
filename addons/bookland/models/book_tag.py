import random

from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api
from datetime import date


class BooklandBookTag(models.Model):
    # Model Attributes
    _name = "bookland.book.tag"
    _description = "Book Tag"

    # Fields
    name = fields.Char(
        string="Book Title",
        help="Store the title of the book",
        translate=True,
        required=True,
        index=True,
        size=512,
    )
