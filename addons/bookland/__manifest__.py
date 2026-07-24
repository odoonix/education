# pylint: disable=W0104

{
    "name": "Book land a modern library management system",
    "website": "https://github.com/odoonix/education",
    "author": "Odoonix",
    "license": "LGPL-3",
    "depends":["website"],
    "data": [
        # Security
        "security/bookland_security.xml",
        "security/ir.model.access.csv",
        # Views
        "views/books_template.xml",
        "views/book_views.xml",
        # Datas
        "datas/menu_website.xml",
    ],
}
