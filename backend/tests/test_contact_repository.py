from app.models.contact import Contact
from app.repositories.contact import ContactRepository


def test_create_contact(db_session):
    repo = ContactRepository(db_session)

    contact = Contact(
        odoo_id=999,
        name="Test User",
        email="test@example.com",
        phone="123456",
        mobile="987654",
    )

    result = repo.create(contact)

    db_session.commit()

    assert result.id is not None
    assert result.email == "test@example.com"
