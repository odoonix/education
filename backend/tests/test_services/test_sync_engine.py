from repositories.contact_repository import ContactRepository
from mappers.contact_mapper import map_contact
from services.sync_engine import SyncEngine


def _fake_pages(pages: list[list[dict]]):
    """یه fetch_page_fn فِیک می‌سازه که صفحه‌به‌صفحه از روی لیست از پیش تعریف‌شده جواب می‌ده."""
    def fetch(offset, limit):
        page_index = offset // limit
        return pages[page_index] if page_index < len(pages) else []
    return fetch


def test_sync_engine_processes_all_records_successfully(db_session):
    repo = ContactRepository(db_session)
    records = [{"id": i, "name": f"User {i}", "email": None, "phone": None, "mobile": None} for i in range(1, 6)]

    engine = SyncEngine(
        session=db_session,
        operation_type="test_sync",
        count_fn=lambda: len(records),
        fetch_page_fn=_fake_pages([records]),
        map_fn=map_contact,
        upsert_fn=repo.upsert,
        batch_size=10,
    )

    result = engine.run()

    assert result["records_fetched"] == 5
    assert result["records_created"] == 5
    assert result["errors_count"] == 0
    assert result["status"] == "success"


def test_sync_engine_continues_after_single_record_failure(db_session):
    """
    این مهم‌ترین تسته: یه رکورد وسط لیست عمداً بی‌فیلد name (اجباری) می‌ذاریم
    تا خطا بده، و چک می‌کنیم بقیه رکوردها همچنان sync بشن.
    """
    repo = ContactRepository(db_session)
    records = [
        {"id": 1, "name": "Good 1", "email": None, "phone": None, "mobile": None},
        {"id": 2, "name": None, "email": None, "phone": None, "mobile": None},  # name اجباریه، None باعث خطا میشه
        {"id": 3, "name": "Good 2", "email": None, "phone": None, "mobile": None},
    ]

    engine = SyncEngine(
        session=db_session,
        operation_type="test_sync_with_errors",
        count_fn=lambda: len(records),
        fetch_page_fn=_fake_pages([records]),
        map_fn=map_contact,
        upsert_fn=repo.upsert,
        batch_size=10,
    )

    result = engine.run()

    assert result["records_fetched"] == 3
    assert result["records_created"] == 2
    assert result["errors_count"] == 1
    assert result["status"] == "completed_with_errors"

    # مطمئن می‌شیم رکوردهای سالم قبل و بعد از رکورد خراب واقعاً ذخیره شدن
    assert repo.get_by_odoo_id(1) is not None
    assert repo.get_by_odoo_id(2) is None
    assert repo.get_by_odoo_id(3) is not None


def test_sync_engine_paginates_across_multiple_pages(db_session):
    """چک می‌کنیم اگه داده بیشتر از یه batch باشه، همه‌ی صفحات خونده می‌شن."""
    repo = ContactRepository(db_session)
    page1 = [{"id": i, "name": f"User {i}", "email": None, "phone": None, "mobile": None} for i in range(1, 4)]
    page2 = [{"id": i, "name": f"User {i}", "email": None, "phone": None, "mobile": None} for i in range(4, 6)]

    engine = SyncEngine(
        session=db_session,
        operation_type="test_pagination",
        count_fn=lambda: 5,
        fetch_page_fn=_fake_pages([page1, page2]),
        map_fn=map_contact,
        upsert_fn=repo.upsert,
        batch_size=3,   # صفحه اول ۳ تا، صفحه دوم ۲ تا
    )

    result = engine.run()

    assert result["records_fetched"] == 5
    assert result["records_created"] == 5


def test_sync_engine_stops_gracefully_on_empty_page(db_session):
    """اگه count_fn عدد اشتباه بزرگ‌تری بده ولی داده واقعی تموم شده باشه، نباید بی‌نهایت loop بزنه."""
    repo = ContactRepository(db_session)
    records = [{"id": 1, "name": "Only One", "email": None, "phone": None, "mobile": None}]

    engine = SyncEngine(
        session=db_session,
        operation_type="test_empty_page",
        count_fn=lambda: 100,  # عمداً غلط، بیشتر از داده واقعی
        fetch_page_fn=_fake_pages([records]),  # فقط یه صفحه داریم، بعدش [] برمی‌گرده
        map_fn=map_contact,
        upsert_fn=repo.upsert,
        batch_size=10,
    )

    result = engine.run()
    assert result["records_fetched"] == 1  # نباید گیر کنه یا خطا بده


def test_sync_engine_counts_updates_correctly_on_rerun(db_session):
    """اجرای دوباره روی همون داده باید records_updated رو افزایش بده، نه records_created."""
    repo = ContactRepository(db_session)
    records = [{"id": 1, "name": "User", "email": None, "phone": None, "mobile": None}]

    def make_engine():
        return SyncEngine(
            session=db_session,
            operation_type="test_rerun",
            count_fn=lambda: len(records),
            fetch_page_fn=_fake_pages([records]),
            map_fn=map_contact,
            upsert_fn=repo.upsert,
            batch_size=10,
        )

    make_engine().run()
    result2 = make_engine().run()

    assert result2["records_created"] == 0
    assert result2["records_updated"] == 1