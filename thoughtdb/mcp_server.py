from mcp.server.fastmcp import FastMCP

# Module-level reference — set by serve_mcp()
_tdb = None


def create_mcp_server(thoughtdb_instance):
    """Create an MCP server wired to a ThoughtDB instance."""
    global _tdb
    _tdb = thoughtdb_instance

    mcp = FastMCP("ThoughtDB")

    @mcp.tool()
    def search(query: str, table: str = None, limit: int = 10) -> list[dict]:
        """Semantic search across database tables. Returns matching rows ranked by similarity."""
        return _tdb.search(query, table=table, limit=limit)

    @mcp.tool()
    def describe() -> dict:
        """Describe all vectorized tables, their columns, and sync status."""
        info = {}
        for table_name, config in _tdb.vectors.items():
            state = _tdb.index.get_sync_state(table_name)
            info[table_name] = {
                "columns": config["columns"],
                "key": config.get("key", "id"),
                "indexed_rows": _tdb.index.count(table_name),
                "last_sync": state.get("last_sync"),
            }
        return info

    @mcp.tool()
    def sync() -> dict:
        """Trigger a sync of all source tables. Embeds new/changed rows."""
        stats = _tdb.sync()
        return {"synced": stats}

    @mcp.tool()
    def query(sql: str, params: list = None) -> list[dict]:
        """Run a read-only SQL query against the source database."""
        result = _tdb.db.fetch(sql, params, limit=100)
        if result is None:
            return []
        return result.records

    @mcp.tool()
    def tables() -> list[str]:
        """List all vectorized table names."""
        return list(_tdb.vectors.keys())

    return mcp


def serve_mcp(thoughtdb_instance, transport="stdio"):
    """Start the MCP server."""
    mcp = create_mcp_server(thoughtdb_instance)
    mcp.run(transport=transport)
