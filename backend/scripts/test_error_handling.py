
from database.session import SessionLocal
from repositories.contact_repository import ContactRepository
from mappers.contact_mapper import map_contact
from services.sync_engine import SyncEngine
from core.entities import ContactEntity


def fake_fetch_page(offset, limit):

    if offset > 0:
        return []
    return [
        {"id": 90001, "name": "Good Record 1", "email": "good1@test.com", "phone": None, "mobile": None},
        {"id": 90002, "name": "Good Record 2", "email": "good2@test.com", "phone": None, "mobile": None},
        {"id": 90003, "name": "Bad Record",    "email": "x" * 500,          "phone": None, "mobile": None},
        {"id": 90004, "name": "Good Record 3", "email": "good3@test.com", "phone": None, "mobile": None},
        {"id": 90005, "name": "Good Record 4", "email": "good4@test.com", "phone": None, "mobile": None},
    ]


def fake_count():
    return 5


session = SessionLocal()
repo = ContactRepository(session)

engine = SyncEngine(
    session=session,
    operation_type="test_error_handling",
    count_fn=fake_count,
    fetch_page_fn=fake_fetch_page,
    map_fn=map_contact,
    upsert_fn=repo.upsert,
    batch_size=10,
)

result = engine.run()
print("Result:", result)

# حالا چک می‌کنیم رکوردهای سالم واقعاً ذخیره شدن
for odoo_id in [90001, 90002, 90003, 90004, 90005]:
    c = repo.get_by_odoo_id(odoo_id)
    print(f"odoo_id={odoo_id}: {'EXISTS' if c else 'MISSING'}")

session.close()