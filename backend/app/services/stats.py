from dataclasses import dataclass


@dataclass
class SyncStats:
    fetched: int = 0
    created: int = 0
    updated: int = 0
    failed: int = 0

    def as_dict(self) -> dict:
        return {
            "fetched": self.fetched,
            "created": self.created,
            "updated": self.updated,
            "failed": self.failed,
        }

    def merge(self, other: "SyncStats") -> None:
        self.fetched += other.fetched
        self.created += other.created
        self.updated += other.updated
        self.failed += other.failed
