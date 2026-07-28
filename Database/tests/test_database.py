import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .. import Database


def test_concurrent_reads_and_writes(tmp_path: Path) -> None:
    database_path = tmp_path / "concurrency_test.db"

    setup_database = Database(database_path)
    setup_database.execute_write("""
        CREATE TABLE memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL UNIQUE
        )
    """)

    writer_count = 4
    reader_count = 6
    writes_per_writer = 100
    reads_per_reader = 150

    expected_rows = writer_count * writes_per_writer

    # Makes all readers and writers begin at roughly the same time.
    start_barrier = threading.Barrier(
        writer_count + reader_count
    )

    def writer(writer_id: int) -> None:
        # Simulates an independent agent.
        database = Database(database_path)

        start_barrier.wait()

        for memory_number in range(writes_per_writer):
            database.execute_write(
                """
                INSERT INTO memories (content)
                VALUES (?)
                """,
                (
                    f"writer-{writer_id}-memory-{memory_number}",
                ),
            )

            # Encourages thread switching so reads and writes overlap.
            time.sleep(0.001)

    def reader(reader_id: int) -> None:
        # Simulates an independent retrieval agent.
        database = Database(database_path)

        start_barrier.wait()

        previous_count = 0

        for _ in range(reads_per_reader):
            rows = database.execute_read(
                "SELECT COUNT(*) AS count FROM memories"
            )

            current_count = rows[0]["count"]

            # Since rows are only inserted, the count must never decrease.
            assert current_count >= previous_count
            previous_count = current_count

            time.sleep(0.001)

    with ThreadPoolExecutor(
        max_workers=writer_count + reader_count
    ) as executor:
        futures = []

        for writer_id in range(writer_count):
            futures.append(
                executor.submit(writer, writer_id)
            )

        for reader_id in range(reader_count):
            futures.append(
                executor.submit(reader, reader_id)
            )

        # Calling result() propagates exceptions from worker threads.
        for future in futures:
            future.result()

    final_rows = setup_database.execute_read(
        """
        SELECT id, content
        FROM memories
        ORDER BY id
        """
    )

    assert len(final_rows) == expected_rows

    contents = {
        row["content"]
        for row in final_rows
    }

    assert len(contents) == expected_rows