from app.domain.entities.contact import Contact


def test_create_contact():
    contact = Contact(
        odoo_id=1,
        name="Ali Ahmadi",
        email="ali@example.com",
        phone="02112345678",
        mobile="09121234567",
    )

    assert contact.odoo_id == 1
    assert contact.name == "Ali Ahmadi"
    assert contact.email == "ali@example.com"
    assert contact.phone == "02112345678"
    assert contact.mobile == "09121234567"
    