from tina4_python.Database import Database
from thoughtdb.embedder import Embedder
from thoughtdb.index import Index
from thoughtdb.sync import Sync
from thoughtdb.mcp_server import create_mcp_server, serve_mcp


class ThoughtDB:
    """Vector API layer that plugs into any relational database.

    Usage:
        tdb = ThoughtDB(
            dsn="sqlite3:my_app.db",
            vectors={
                "products": {"columns": ["name", "description"], "key": "id"},
                "customers": {"columns": ["bio"], "key": "customer_id"},
            }
        )
        results = tdb.search("running shoes")
    """

    def __init__(self, dsn, vectors, username="", password="",
                 model_path="./models_db/nomic-embed-text-v1.5.Q4_K_M.gguf",
                 index_path="./thoughtdb.index",
                 auto_sync=True):
        """
        dsn: tina4 connection string (e.g. "sqlite3:app.db", "psycopg2:localhost/5432:mydb")
        vectors: dict of {table: {columns: [...], key: "id"}}
        username: DB username (if needed)
        password: DB password (if needed)
        model_path: path to GGUF embedding model
        index_path: path for the sidecar index file
        auto_sync: run initial sync on startup
        """
        self.db = Database(dsn, username, password)
        self.embedder = Embedder(model_path)
        self.index = Index(index_path, dimensions=self.embedder.dimensions)
        self.vectors = vectors
        self.sync_engine = Sync(self.db, self.index, self.embedder, vectors)

        if auto_sync:
            self.sync()

    def search(self, query, table=None, limit=10):
        """Semantic search across vectorized tables.

        Returns source rows from the database with similarity scores.
        """
        query_vector = self.embedder.embed(query)
        hits = self.index.search(query_vector, k=limit, table_name=table)

        if not hits:
            return []

        # Group hits by source table
        by_table = {}
        for hit in hits:
            t = hit["table_name"]
            if t not in by_table:
                by_table[t] = []
            by_table[t].append(hit)

        # Fetch actual rows from source DB
        results = []
        for table_name, table_hits in by_table.items():
            config = self.vectors.get(table_name)
            if not config:
                continue
            key = config.get("key", "id")

            # Build IN clause
            key_values = [h["key_value"] for h in table_hits]
            placeholders = ", ".join(["?" for _ in key_values])
            sql = f"select * from {table_name} where {key} in ({placeholders})"
            result = self.db.fetch(sql, key_values, limit=len(key_values))

            if result is None:
                continue

            # Build lookup for distances
            dist_map = {h["key_value"]: h["distance"] for h in table_hits}

            for record in result.records:
                row = dict(record)
                row["_table"] = table_name
                row["_distance"] = dist_map.get(str(record[key]), None)
                # Convert L2 distance to 0-100 similarity score
                # Lower distance = more similar; score = 100 / (1 + distance)
                d = row["_distance"] or 0
                row["_score"] = round(100 / (1 + d), 1)
                results.append(row)

        # Sort by score descending
        results.sort(key=lambda r: r.get("_score", 0), reverse=True)
        return results[:limit]

    def sync(self):
        """Sync all configured tables into the vector index."""
        return self.sync_engine.sync_all()

    def resync(self, table=None):
        """Full resync - drops and re-embeds a table (or all tables)."""
        return self.sync_engine.full_resync(table)

    def status(self):
        """Get sync status for all configured tables."""
        return self.sync_engine.status()

    def serve_mcp(self, transport="stdio"):
        """Start an MCP server so LLMs can query this database."""
        serve_mcp(self, transport=transport)

    def close(self):
        """Close all connections."""
        self.db.close()
        self.index.close()
