import sqlite3

import pytest

from Database.Database import Database
from Apps.Planner.Planner import Planner


@pytest.fixture
def database(tmp_path):
    return Database(tmp_path / "planner.db")


@pytest.fixture
def planner(database):
    return Planner(database)


def test_create_lane_writes_inserted_rev(planner, database):
    lane_id = planner.create_lane("Test lane", "Fake data", 1, 1, "aida")

    revs = database.execute_read(
        "SELECT event, name, created_by FROM lanes_rev WHERE id = ?",
        (lane_id,),
    )

    assert revs == [{"event": "inserted", "name": "Test lane", "created_by": "aida"}]


def test_lane_cannot_be_deleted(planner, database):
    lane_id = planner.create_lane("Test lane", "Fake data", 1, 1, "aida")

    with pytest.raises(sqlite3.IntegrityError, match="never deleted"):
        database.execute_write("DELETE FROM lanes WHERE id = ?", (lane_id,))