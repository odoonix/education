import random

from attr import field
import logging

from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, Command
from datetime import date

_logger = logging.getLogger(__name__)

class BooklandBook(models.Model):
    # Model Attributes
    _name = "bookland.book"
    _inherit = ['image.mixin']
    _description = "Book"

    # Fields
    name = fields.Char(
        string="Book Title",
        help="Store the title of the book",
        translate=True,
        required=True,
        index=True,
        size=512,
    )

    active = fields.Boolean(default="True")

    display_name = fields.Char(
        string="Book Display Title",
        translate=True,
    )
    description = fields.Html(
        # string="Description"
        required=False,
        translate=True,
        index=False,
    )
    publish_date = fields.Date(string="Publish")

    # time_to_market_date = {
    #     "type": "date",
    #     "name": "present_date",
    #     "note": "This is when the book is present to market"
    # }
    time_to_market_date = fields.Date(required=False)

    price = fields.Float(
        string="Book Price",
    )

    age_in_days = fields.Integer(
        string="Days Since Publish",
        compute="_compute_age_in_days",  # the function computed
        store=True,
    )

    tag_ids = fields.Many2many("bookland.book.tag")

    @api.onchange("publish_date")
    def _compute_age_in_days(self):
        for record in self:
            if record.publish_date:
                delta = date.today() - record.publish_date
                record.age_in_days = delta.days
            else:
                record.age_in_days = 0

    @api.model
    def action_create_random_book(self, *args, **kwargs):
        self.env["bookland.book"].create({
            "name": "Name" + str(random.randint(0, 1500)),
            "description": "",
            "tag_ids": [Command.create({
                "name": "tag1"
            })]
        })

    @api.model
    def action_test_erro(self, *args, **kwargs):
        # self.ensore_once()
        raise UserError("There is something bad")

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            record.update({
                "display_name": f"Book {record.name}"
            })
        # self.unlink()


    # def _get_bookss_name(self, parents):
    #     names = parents.mapped('name')
    #     return names
    

    def create(self,vals_list):
        res = super().create(vals_list)

        grouped_result = self.read_group(
            [], #domain
            ['name', 'price:sum'], #fields
            ['name'] #group_by
            )


        # Search
        # all_record = self.env['bookland.book'].search([],order='publish_date asc')
        # names=self._get_bookss_name(all_record)
        # record12 = self.env['bookland.book'].browse(1)
        # for record in all_record:
        #     _logger.info(record.name)
        # Logs vals_list
        for val in vals_list:
            _logger.info(val)
        return res
    
    def write(self,vals_list):
        res = super().write(vals_list)
        for val in vals_list:
            _logger.info(val)
        return res