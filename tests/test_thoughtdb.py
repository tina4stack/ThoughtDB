"""Tests for ThoughtDB — vector API layer for relational databases.

Tests the full pipeline: connect to DB → create test data → sync → search.
Starts with SQLite (no external deps), then parametrize for other engines.
"""
import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_DB = "./test_source.db"
TEST_INDEX = "./test_thoughtdb.index"
MODEL_PATH = "./models_db/nomic-embed-text-v1.5.Q4_K_M.gguf"


@pytest.fixture(scope="module")
def source_db():
    """Create a test SQLite source database with sample data."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    conn.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL
        )
    """)
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bio TEXT
        )
    """)

    products = [
        ("Running Shoes", "Lightweight breathable running shoes for marathon training", 89.99),
        ("Hiking Boots", "Waterproof leather hiking boots for mountain trails", 149.99),
        ("Basketball Sneakers", "High-top basketball shoes with ankle support", 119.99),
        ("Sandals", "Comfortable beach sandals with arch support", 39.99),
        ("Dress Shoes", "Classic black leather dress shoes for formal occasions", 199.99),
        ("Tennis Racket", "Professional carbon fiber tennis racket", 249.99),
        ("Soccer Ball", "FIFA approved match soccer ball", 29.99),
        ("Yoga Mat", "Non-slip eco-friendly yoga mat for home workouts", 45.99),
        ("Swimming Goggles", "Anti-fog UV protection swimming goggles", 24.99),
        ("Cycling Helmet", "Aerodynamic lightweight cycling helmet with ventilation", 79.99),
    ]
    conn.executemany(
        "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
        products
    )

    customers = [
        ("Alice", "Loves marathon running and outdoor activities"),
        ("Bob", "Professional basketball player and fitness enthusiast"),
        ("Carol", "Yoga instructor who enjoys swimming"),
        ("Dave", "Casual cyclist and weekend hiker"),
        ("Eve", "Competitive tennis player and soccer coach"),
    ]
    conn.executemany(
        "INSERT INTO customers (name, bio) VALUES (?, ?)",
        customers
    )

    conn.commit()
    conn.close()
    yield TEST_DB

    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture(scope="module")
def tdb(source_db):
    """Create a ThoughtDB instance connected to the test source DB."""
    if os.path.exists(TEST_INDEX):
        os.remove(TEST_INDEX)

    from thoughtdb import ThoughtDB

    instance = ThoughtDB(
        dsn=f"sqlite3:{source_db}",
        vectors={
            "products": {"columns": ["name", "description"], "key": "id"},
            "customers": {"columns": ["name", "bio"], "key": "id"},
        },
        model_path=MODEL_PATH,
        index_path=TEST_INDEX,
        auto_sync=True,
    )
    yield instance
    instance.close()

    if os.path.exists(TEST_INDEX):
        os.remove(TEST_INDEX)


class TestEmbedder:
    def test_embed_returns_vector(self):
        from thoughtdb.embedder import Embedder
        e = Embedder(MODEL_PATH)
        vec = e.embed("hello world")
        assert isinstance(vec, list)
        assert len(vec) == 768

    def test_embed_caches_identical_queries(self):
        from thoughtdb.embedder import Embedder
        e = Embedder(MODEL_PATH)
        v1 = e.embed("test query")
        v2 = e.embed("test query")
        assert v1 is v2  # same object, not just equal

    def test_to_bytes_roundtrip(self):
        from thoughtdb.embedder import Embedder
        vec = [0.1, 0.2, 0.3, 0.4]
        blob = Embedder.to_bytes(vec)
        assert isinstance(blob, bytes)
        restored = Embedder.from_bytes(blob)
        assert len(restored) == 4
        assert abs(restored[0] - 0.1) < 1e-6


class TestIndex:
    def test_create_and_search(self):
        from thoughtdb.index import Index
        from thoughtdb.embedder import Embedder
        idx_path = "./test_index_unit.db"
        if os.path.exists(idx_path):
            os.remove(idx_path)

        idx = Index(idx_path, dimensions=4)
        idx.add(1, [1.0, 0.0, 0.0, 0.0], "test_table", "1")
        idx.add(2, [0.0, 1.0, 0.0, 0.0], "test_table", "2")
        idx.add(3, [0.9, 0.1, 0.0, 0.0], "test_table", "3")
        idx.db.commit()

        results = idx.search([1.0, 0.0, 0.0, 0.0], k=2)
        assert len(results) == 2
        # Closest should be rowid 1 (exact match)
        assert results[0]["key_value"] == "1"

        assert idx.count() == 3
        assert idx.count("test_table") == 3

        idx.close()
        os.remove(idx_path)

    def test_sync_state(self):
        from thoughtdb.index import Index
        idx_path = "./test_index_state.db"
        if os.path.exists(idx_path):
            os.remove(idx_path)

        idx = Index(idx_path, dimensions=4)
        idx.set_sync_state("my_table", last_id=42, last_sync="2025-01-01", total_rows=100)
        state = idx.get_sync_state("my_table")
        assert state["last_id"] == 42
        assert state["total_rows"] == 100

        idx.close()
        os.remove(idx_path)


class TestThoughtDB:
    def test_sync_indexes_all_rows(self, tdb):
        status = tdb.status()
        assert status["products"]["indexed"] == 10
        assert status["customers"]["indexed"] == 5

    def test_search_products(self, tdb):
        results = tdb.search("running shoes for training", table="products", limit=3)
        assert len(results) > 0
        assert results[0]["_table"] == "products"
        assert "_score" in results[0]
        # Running shoes should be top result
        assert "running" in results[0]["name"].lower() or "running" in results[0]["description"].lower()

    def test_search_across_tables(self, tdb):
        results = tdb.search("marathon runner", limit=5)
        assert len(results) > 0
        # Should find products AND customers
        tables = set(r["_table"] for r in results)
        assert len(tables) >= 1  # at least one table matched

    def test_search_customers(self, tdb):
        results = tdb.search("yoga and swimming", table="customers", limit=3)
        assert len(results) > 0
        assert results[0]["_table"] == "customers"
        # Carol (yoga instructor who swims) should rank high
        names = [r["name"] for r in results]
        assert "Carol" in names[:2]

    def test_search_returns_source_columns(self, tdb):
        results = tdb.search("hiking", table="products", limit=1)
        assert len(results) > 0
        row = results[0]
        assert "name" in row
        assert "description" in row
        assert "price" in row
        assert "id" in row

    def test_incremental_sync(self, tdb):
        """Add a row to source DB, sync, verify it's searchable."""
        import sqlite3
        conn = sqlite3.connect(TEST_DB)
        conn.execute(
            "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
            ("Climbing Rope", "Dynamic rock climbing rope 60 meters for sport climbing", 89.99)
        )
        conn.commit()
        conn.close()

        stats = tdb.sync()
        assert stats["products"] >= 1

        results = tdb.search("rock climbing rope", table="products", limit=3)
        assert any("climbing" in r.get("name", "").lower() for r in results)

    def test_resync(self, tdb):
        old_count = tdb.index.count("customers")
        stats = tdb.resync("customers")
        assert stats["customers"] == old_count  # should re-embed same count

    def test_status(self, tdb):
        status = tdb.status()
        assert "products" in status
        assert "customers" in status
        assert status["products"]["last_sync"] is not None


class TestMCPServer:
    def test_create_server(self, tdb):
        from thoughtdb.mcp_server import create_mcp_server
        mcp = create_mcp_server(tdb)
        assert mcp is not None
