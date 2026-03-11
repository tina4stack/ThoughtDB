import os
import sqlite3
import struct
import sqlite_vec


class Index:
    """Sidecar sqlite-vec index. Stores vectors in a separate .db file,
    keyed back to source tables via (table_name, key_value)."""

    def __init__(self, path="./thoughtdb.index", dimensions=768):
        self.path = path
        self.dimensions = dimensions
        self.db = sqlite3.connect(path)
        self.db.enable_load_extension(True)
        sqlite_vec.load(self.db)
        self.db.enable_load_extension(False)
        self._create_tables()

    def _create_tables(self):
        """Create the vec0 virtual table and sync state table."""
        self.db.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_store USING vec0(
                embedding float[{self.dimensions}],
                table_name TEXT,
                key_value TEXT
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS sync_state (
                table_name TEXT PRIMARY KEY,
                last_id INTEGER DEFAULT 0,
                last_sync TEXT,
                total_rows INTEGER DEFAULT 0
            )
        """)
        self.db.commit()

    def add(self, rowid, vector, table_name, key_value):
        """Add a vector to the index."""
        blob = _serialize(vector)
        self.db.execute(
            "INSERT OR REPLACE INTO vec_store(rowid, embedding, table_name, key_value) VALUES (?, ?, ?, ?)",
            [rowid, blob, table_name, str(key_value)]
        )

    def add_batch(self, rows):
        """Add multiple vectors. rows = list of (rowid, vector, table_name, key_value)."""
        self.db.executemany(
            "INSERT OR REPLACE INTO vec_store(rowid, embedding, table_name, key_value) VALUES (?, ?, ?, ?)",
            [(r[0], _serialize(r[1]), r[2], str(r[3])) for r in rows]
        )
        self.db.commit()

    def search(self, query_vector, k=10, table_name=None):
        """Search for similar vectors. Returns list of {table_name, key_value, distance}."""
        blob = _serialize(query_vector)
        if table_name:
            cursor = self.db.execute(
                """SELECT rowid, table_name, key_value, distance
                   FROM vec_store
                   WHERE embedding MATCH ? AND k = ? AND table_name = ?""",
                [blob, k, table_name]
            )
        else:
            cursor = self.db.execute(
                """SELECT rowid, table_name, key_value, distance
                   FROM vec_store
                   WHERE embedding MATCH ? AND k = ?""",
                [blob, k]
            )
        results = []
        for row in cursor.fetchall():
            results.append({
                "rowid": row[0],
                "table_name": row[1],
                "key_value": row[2],
                "distance": row[3]
            })
        return results

    def delete(self, table_name, key_value=None):
        """Delete vectors for a table (or specific key)."""
        if key_value is not None:
            self.db.execute(
                "DELETE FROM vec_store WHERE table_name = ? AND key_value = ?",
                [table_name, str(key_value)]
            )
        else:
            self.db.execute(
                "DELETE FROM vec_store WHERE table_name = ?",
                [table_name]
            )
        self.db.commit()

    def count(self, table_name=None):
        """Count indexed vectors."""
        if table_name:
            row = self.db.execute(
                "SELECT count(*) FROM vec_store WHERE table_name = ?", [table_name]
            ).fetchone()
        else:
            row = self.db.execute("SELECT count(*) FROM vec_store").fetchone()
        return row[0] if row else 0

    def get_sync_state(self, table_name):
        """Get sync state for a table."""
        row = self.db.execute(
            "SELECT last_id, last_sync, total_rows FROM sync_state WHERE table_name = ?",
            [table_name]
        ).fetchone()
        if row:
            return {"last_id": row[0], "last_sync": row[1], "total_rows": row[2]}
        return {"last_id": 0, "last_sync": None, "total_rows": 0}

    def set_sync_state(self, table_name, last_id=0, last_sync=None, total_rows=0):
        """Update sync state for a table."""
        self.db.execute(
            """INSERT OR REPLACE INTO sync_state(table_name, last_id, last_sync, total_rows)
               VALUES (?, ?, ?, ?)""",
            [table_name, last_id, last_sync, total_rows]
        )
        self.db.commit()

    def close(self):
        self.db.close()


def _serialize(vector):
    """Convert float list/array to bytes for sqlite-vec."""
    if isinstance(vector, bytes):
        return vector
    return struct.pack(f"{len(vector)}f", *vector)
