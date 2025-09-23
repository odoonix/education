# pylint: disable=W0104

{
    "name": "Book land a modern library management system",
    "website": "https://github.com/odoonix/education",
    "author": "Odoonix",
    "license": "LGPL-3",
    "application": True,
    "depends": ["base"],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/book_views.xml",
        "views/loan_views.xml",
        "views/partner_views.xml",
    ],
}
