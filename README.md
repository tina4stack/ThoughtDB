# ThoughtDB

**Vector API layer that plugs into any relational database.**

ThoughtDB adds semantic search to your existing database without modifying it. Point it at any relational database (SQLite, Postgres, MySQL, Firebird, MSSQL), tell it which tables and columns to vectorize, and it handles the rest — embedding, indexing, and search. Built-in MCP server lets LLMs query your data directly.

```python
from thoughtdb import ThoughtDB

tdb = ThoughtDB(
    dsn="sqlite3:my_app.db",
    vectors={
        "products": {"columns": ["name", "description"], "key": "id"},
        "customers": {"columns": ["bio"], "key": "customer_id"},
    }
)

results = tdb.search("comfortable running shoes")
# Returns actual rows from your database, ranked by similarity
```

## How It Works

```
Your App
   │
   ├── Source Database (any relational DB) ──── never modified
   │      SQLite / Postgres / MySQL / Firebird / MSSQL
   │
   ├── ThoughtDB
   │      ├── Sidecar Index (sqlite-vec) ──── separate .index file
   │      ├── Embedder (Nomic Embed v1.5) ── 768-dim vectors
   │      └── Sync Engine ──── auto-detects new/changed rows
   │
   └── MCP Server ──── LLMs talk to your data
```

**Key principle:** Your source database is never modified. ThoughtDB maintains its own sidecar index file alongside your database. This means you can add vector search to production databases with zero risk.

## Installation

```bash
pip install thoughtdb
```

Or with `uv`:
```bash
uv add thoughtdb
```

### Database Drivers

Install the driver for your database:

```bash
# PostgreSQL
pip install thoughtdb[postgres]

# MySQL
pip install thoughtdb[mysql]

# Firebird
pip install thoughtdb[firebird]

# MSSQL
pip install thoughtdb[mssql]

# SQLite — built in, no extra driver needed
```

### Embedding Model

Download a GGUF embedding model (default: Nomic Embed Text v1.5):

```bash
mkdir -p models_db
curl -L -o models_db/nomic-embed-text-v1.5.Q4_K_M.gguf \
  "https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q4_K_M.gguf"
```

## Quick Start

### 1. Connect to your database

```python
from thoughtdb import ThoughtDB

# SQLite
tdb = ThoughtDB(dsn="sqlite3:my_app.db", vectors={...})

# PostgreSQL
tdb = ThoughtDB(dsn="psycopg2:localhost/5432:mydb", vectors={...},
                username="user", password="pass")

# MySQL
tdb = ThoughtDB(dsn="mysql:localhost/3306:mydb", vectors={...},
                username="user", password="pass")
```

### 2. Configure what to vectorize

```python
tdb = ThoughtDB(
    dsn="sqlite3:shop.db",
    vectors={
        # Table name -> columns to embed + primary key
        "products": {
            "columns": ["name", "description"],
            "key": "id"
        },
        "articles": {
            "columns": ["title", "body"],
            "key": "article_id"
        },
    }
)
# ThoughtDB automatically syncs on startup — no manual embed() calls
```

### 3. Search

```python
# Search across all vectorized tables
results = tdb.search("wireless headphones")

# Search a specific table
results = tdb.search("wireless headphones", table="products", limit=5)

# Each result is the actual database row + similarity metadata
for r in results:
    print(f"{r['name']} (score: {r['_score']}, table: {r['_table']})")
```

### 4. Keep in sync

```python
# Incremental sync — picks up new/changed rows automatically
tdb.sync()

# Full resync — re-embeds everything (e.g. after model change)
tdb.resync()
tdb.resync("products")  # resync one table

# Check sync status
status = tdb.status()
# {'products': {'last_id': 150, 'last_sync': '2025-...', 'indexed': 150, 'total_rows': 150}}
```

## MCP Server — Let LLMs Query Your Data

ThoughtDB includes a built-in [Model Context Protocol](https://modelcontextprotocol.io/) server. This lets any MCP-compatible LLM (Claude, GPT, etc.) search and query your database directly.

### Start the MCP server

```python
tdb = ThoughtDB(dsn="sqlite3:my_app.db", vectors={...})
tdb.serve_mcp()  # stdio transport (default)
```

### Configure in Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-database": {
      "command": "python",
      "args": ["my_mcp_server.py"]
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `search(query, table?, limit?)` | Semantic search across vectorized tables |
| `describe()` | List all vectorized tables with status |
| `sync()` | Trigger incremental sync |
| `query(sql, params?)` | Run read-only SQL against source database |
| `tables()` | List vectorized table names |

Once configured, you can ask Claude things like:
- *"Find products similar to running shoes"*
- *"Show me customers interested in outdoor activities"*
- *"What's the most expensive product in the hiking category?"*

## API Reference

### `ThoughtDB(dsn, vectors, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dsn` | `str` | required | Database connection string (tina4 format) |
| `vectors` | `dict` | required | Tables to vectorize: `{table: {columns: [...], key: "id"}}` |
| `username` | `str` | `""` | Database username |
| `password` | `str` | `""` | Database password |
| `model_path` | `str` | `"./models_db/nomic-embed-text-v1.5.Q4_K_M.gguf"` | Embedding model path |
| `index_path` | `str` | `"./thoughtdb.index"` | Sidecar index file path |
| `auto_sync` | `bool` | `True` | Run initial sync on startup |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `search(query, table=None, limit=10)` | `list[dict]` | Semantic search. Returns source DB rows with `_score`, `_distance`, `_table` |
| `sync()` | `dict` | Incremental sync. Returns `{table: rows_synced}` |
| `resync(table=None)` | `dict` | Full resync (drop + re-embed) |
| `status()` | `dict` | Sync status per table |
| `serve_mcp(transport="stdio")` | - | Start MCP server |
| `close()` | - | Close all connections |

### DSN Formats

| Database | DSN Format |
|----------|-----------|
| SQLite | `sqlite3:path/to/db.db` |
| PostgreSQL | `psycopg2:host/port:dbname` |
| MySQL | `mysql:host/port:dbname` |
| Firebird | `firebird:host/port:dbpath` |
| MSSQL | `pymssql:host/port:dbname` |

## Benchmarks

Tested with Madagascar zoo animal data (species descriptions, habitats, behaviors, conservation status).

### 100 Animals

| Metric | ThoughtDB | ChromaDB | FAISS | Qdrant |
|--------|-----------|----------|-------|--------|
| Sync/Insert (s) | 3.69 | 10.54 | **0.15** | 0.47 |
| Peak Memory (MB) | 241.81 | 25.78 | **0.31** | 3.85 |
| Avg Search (ms) | 25.09 | 148.59 | 5.60 | **0.66** |
| Min Search (ms) | 13.43 | 73.88 | **0.01** | 0.41 |
| Max Search (ms) | 54.70 | 680.73 | 55.92 | **2.43** |

### 500 Animals

| Metric | ThoughtDB | ChromaDB | FAISS | Qdrant |
|--------|-----------|----------|-------|--------|
| Sync/Insert (s) | 11.66 | 26.30 | **0.33** | 1.21 |
| Peak Memory (MB) | 242.09 | 24.64 | **1.54** | 6.47 |
| Avg Search (ms) | 14.63 | 116.08 | **0.25** | 1.63 |
| Min Search (ms) | 11.14 | 74.09 | **0.03** | 0.70 |
| Max Search (ms) | 32.97 | 214.28 | **2.25** | 9.15 |

**Notes:**
- FAISS and Qdrant use pre-embedded vectors (no embedding time in sync) — they are pure vector stores
- ThoughtDB and ChromaDB embed during sync (includes embedding time) — they are full-stack solutions
- ThoughtDB's peak memory includes the embedding model (~240MB) — this is loaded once and shared
- ThoughtDB is **2.3x faster** than ChromaDB on sync and **8x faster** on search
- Unlike FAISS/Qdrant, ThoughtDB plugs directly into your existing database — no ETL pipeline needed

### What Each System Is

| System | Type | DB Integration | Built-in Embeddings | Persistence |
|--------|------|----------------|---------------------|-------------|
| **ThoughtDB** | Vector API layer | Any relational DB | Yes | Sidecar file |
| ChromaDB | Standalone vector DB | None (copy data) | Yes | In-memory/persistent |
| FAISS | Vector search library | None | No | None |
| Qdrant | Standalone vector DB | No | Yes (server mode) | In-memory/server |

## Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/test_thoughtdb.py -v

# Run benchmarks
uv run python tests/benchmark.py
```

## Project Structure

```
thoughtdb/
├── __init__.py       # ThoughtDB class — the public API
├── embedder.py       # Model loading + embedding with caching
├── index.py          # Sidecar sqlite-vec index (vec0 virtual table)
├── sync.py           # Change detection & incremental sync engine
└── mcp_server.py     # MCP tool definitions for LLM access
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `tina4-python` | Database abstraction (SQLite, Postgres, MySQL, Firebird, MSSQL) |
| `sqlite-vec` | Vector search via sqlite vec0 virtual tables |
| `thought` | Embedding model loader (GGUF format) |
| `numpy` | Vector math and serialization |
| `mcp` | Model Context Protocol server |

## License

MIT
