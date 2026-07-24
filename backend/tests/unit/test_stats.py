from app.services.stats import SyncStats


def test_default_stats_are_zero():
    stats = SyncStats()
    assert stats.as_dict() == {"fetched": 0, "created": 0, "updated": 0, "failed": 0}


def test_merge_adds_values_together():
    a = SyncStats(fetched=5, created=3, updated=1, failed=1)
    b = SyncStats(fetched=2, created=0, updated=2, failed=0)

    a.merge(b)

    assert a.as_dict() == {"fetched": 7, "created": 3, "updated": 3, "failed": 1}
    assert b.as_dict() == {"fetched": 2, "created": 0, "updated": 2, "failed": 0}
