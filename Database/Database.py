from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable


Parameters = tuple[Any, ...]
Statement = tuple[str, Parameters]


class Database:
    """
    Thread-safe SQLite wrapper for one local application.

    - Separate connection per operation
    - Read-only connections for reads
    - WAL mode for concurrent readers and one writer
    - One shared write lock per database file
    - Atomic multi-statement transactions
    """

    _locks_guard = threading.Lock()
    _write_locks: dict[Path, threading.Lock] = {}

    def __init__(
        self,
        path: str | Path = "database.db",
        timeout: float = 10.0,
    ) -> None:
        self.path = Path(path).resolve()
        self.timeout = timeout

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._write_lock = self._get_write_lock(self.path)
        self._configure_database()

    @classmethod
    def _get_write_lock(
        cls,
        path: Path,
    ) -> threading.Lock:
        """
        All Database instances pointing at the same file
        share one in-process write lock.
        """
        with cls._locks_guard:
            return cls._write_locks.setdefault(
                path,
                threading.Lock(),
            )

    def _connect(
        self,
        *,
        readonly: bool = False,
    ) -> sqlite3.Connection:
        if readonly:
            # as_uri() safely handles absolute paths and spaces.
            uri = f"{self.path.as_uri()}?mode=ro"

            connection = sqlite3.connect(
                uri,
                uri=True,
                timeout=self.timeout,
                isolation_level=None,
            )

            # Additional protection alongside mode=ro.
            connection.execute("PRAGMA query_only = ON")
        else:
            connection = sqlite3.connect(
                self.path,
                timeout=self.timeout,
                isolation_level=None,
            )

        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        return connection

    def _configure_database(self) -> None:
        connection = self._connect()

        try:
            connection.execute("PRAGMA journal_mode = WAL")
        finally:
            connection.close()

    def execute_read(
        self,
        query: str,
        parameters: Parameters = (),
    ) -> list[dict[str, Any]]:
        connection = self._connect(readonly=True)

        try:
            cursor = connection.execute(
                query,
                parameters,
            )

            return [
                dict(row)
                for row in cursor.fetchall()
            ]
        finally:
            connection.close()

    def execute_write(
        self,
        query: str,
        parameters: Parameters = (),
    ) -> int | None:
        """
        Execute one statement as an atomic transaction.
        """
        results = self.execute_transaction([
            (query, parameters),
        ])

        return results[0]

    def execute_transaction(
        self,
        statements: Iterable[Statement],
    ) -> list[int | None]:
        """
        Execute several statements as one all-or-nothing transaction.

        A reader sees either:
        - the state before the transaction, or
        - the complete state after it

        It never sees a partially committed batch.
        """
        statements = list(statements)

        if not statements:
            return []

        with self._write_lock:
            connection = self._connect()

            try:
                connection.execute("BEGIN IMMEDIATE")

                last_row_ids: list[int | None] = []

                for query, parameters in statements:
                    cursor = connection.execute(
                        query,
                        parameters,
                    )
                    last_row_ids.append(cursor.lastrowid)

                connection.commit()
                return last_row_ids

            except Exception:
                connection.rollback()
                raise

            finally:
                connection.close()