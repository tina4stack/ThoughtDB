from datetime import datetime


class Sync:
    """Syncs source database tables into the sidecar vector index."""

    def __init__(self, source_db, index, embedder, vectors_config):
        """
        source_db: tina4_python.Database instance (any DB)
        index: Index instance (sidecar sqlite-vec)
        embedder: Embedder instance
        vectors_config: dict of {table_name: {columns: [...], key: "id"}}
        """
        self.db = source_db
        self.index = index
        self.embedder = embedder
        self.config = vectors_config
        self._rowid_counter = self._get_max_rowid()

    def _get_max_rowid(self):
        """Get the current max rowid in the index."""
        row = self.index.db.execute("SELECT MAX(rowid) FROM vec_store").fetchone()
        return (row[0] or 0)

    def sync_all(self):
        """Sync all configured tables."""
        stats = {}
        for table_name, config in self.config.items():
            count = self.sync_table(table_name, config)
            stats[table_name] = count
        return stats

    def sync_table(self, table_name, config):
        """Sync a single table. Returns number of new rows embedded."""
        columns = config["columns"]
        key = config.get("key", "id")
        sync_column = config.get("sync", key)  # column used for change detection

        state = self.index.get_sync_state(table_name)
        last_id = state["last_id"]

        # Build SELECT: key column + all text columns to embed
        select_cols = [key] + [c for c in columns if c != key]
        col_list = ", ".join(select_cols)

        # Fetch new rows since last sync
        sql = f"select {col_list} from {table_name} where {sync_column} > ?"
        result = self.db.fetch(sql, [last_id], limit=10000)

        if result is None or len(result.records) == 0:
            return 0

        batch = []
        max_id = last_id
        count = 0

        for record in result.records:
            row_key = record[key]

            # Concatenate all configured columns into one text
            text_parts = []
            for col in columns:
                val = record.get(col, "")
                if val is not None and str(val).strip():
                    text_parts.append(str(val))

            if not text_parts:
                continue

            text = " ".join(text_parts)
            vector = self.embedder.embed(text)

            self._rowid_counter += 1
            batch.append((self._rowid_counter, vector, table_name, row_key))
            count += 1

            # Track highest ID for sync state
            try:
                if int(row_key) > max_id:
                    max_id = int(row_key)
            except (ValueError, TypeError):
                max_id = last_id

            # Flush in batches of 100
            if len(batch) >= 100:
                self.index.add_batch(batch)
                batch = []

        # Flush remaining
        if batch:
            self.index.add_batch(batch)

        # Update sync state
        self.index.set_sync_state(
            table_name,
            last_id=max_id,
            last_sync=datetime.now().isoformat(),
            total_rows=state["total_rows"] + count
        )

        return count

    def full_resync(self, table_name=None):
        """Drop and re-embed everything for a table (or all tables)."""
        tables = [table_name] if table_name else list(self.config.keys())
        stats = {}
        for t in tables:
            self.index.delete(t)
            self.index.set_sync_state(t, last_id=0, last_sync=None, total_rows=0)
            count = self.sync_table(t, self.config[t])
            stats[t] = count
        return stats

    def status(self):
        """Get sync status for all configured tables."""
        result = {}
        for table_name in self.config:
            state = self.index.get_sync_state(table_name)
            state["indexed"] = self.index.count(table_name)
            result[table_name] = state
        return result
