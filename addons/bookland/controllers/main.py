from odoo import http, _
from odoo.http import request

class BookController(http.Controller):

    @http.route('/books', type='http', auth="user", website=True)
    def books_details(self):
        book_ids =request.env['bookland.book'].sudo().search([])
        values = {
            'books': book_ids,
        }
        return request.render('bookland.books_details_template', values)