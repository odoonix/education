from services.sync_engine import SyncEngine
from repositories.contact_repository import ContactRepository
from mappers.contact_mapper import map_contact


class FakeShutdownHandler:
    """شبیه‌سازی سیگنال توقف — بلافاصله بعد از اولین batch درخواست توقف می‌ده."""
    def __init__(self):
        self.shutdown_requested = False


def test_sync_engine_stops_after_shutdown_signal(db_session):
    repo = ContactRepository(db_session)
    page1 = [{"id": i, "name": f"U{i}", "email": None, "phone": None, "mobile": None} for i in range(1, 4)]
    page2 = [{"id": i, "name": f"U{i}", "email": None, "phone": None, "mobile": None} for i in range(4, 7)]

    handler = FakeShutdownHandler()

    def fetch(offset, limit):
        pages = [page1, page2]
        idx = offset // limit
        if idx == 0:
            return pages[0]
        handler.shutdown_requested = True  # بعد از batch اول، شبیه‌سازی سیگنال
        return pages[1] if idx < len(pages) else []

    engine = SyncEngine(
        session=db_session,
        operation_type="test_shutdown",
        count_fn=lambda: 6,
        fetch_page_fn=fetch,
        map_fn=map_contact,
        upsert_fn=repo.upsert,
        batch_size=3,
        shutdown_handler=handler,
    )

    result = engine.run()

    assert result["status"] == "interrupted"
    assert result["records_fetched"] == 6   # هر دو batch پردازش شدن قبل از چک شدن پرچم