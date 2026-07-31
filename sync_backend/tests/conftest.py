from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if os.getenv("RUN_DOCKER_TESTS") == "1":
        return
    docker_skip = pytest.mark.skip(reason="Docker-backed test; run through backend-test")
    for item in items:
        if "integration" in item.keywords or "end_to_end" in item.keywords:
            item.add_marker(docker_skip)
