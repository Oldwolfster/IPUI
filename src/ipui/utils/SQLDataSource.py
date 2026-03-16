# SQLDataSource.py  NEW: SQLite data source for PowerGrid

import sqlite3


class SQLDataSource:
    """Encapsulates SQLite queries for PowerGrid.

    Usage:
        src = SQLDataSource("my.db", "SELECT * FROM runs")
        src = SQLDataSource("my.db", table="runs")
        src = SQLDataSource(conn,    "SELECT * FROM runs")
    """

    def __init__(self, source, query=None, table=None):
        self.owns_conn = False
        if isinstance(source, sqlite3.Connection):
            self.conn = source
        else:
            self.conn      = sqlite3.connect(source)
            self.owns_conn = True
        if table and not query:
            query = f"SELECT * FROM {table}"
        if not query:
            from ipui.utils.EZ import EZ
            EZ.err(
                "SQLDataSource needs a query or table. "
                "SQLDataSource('my.db', query='SELECT ...') or "
                "SQLDataSource('my.db', table='runs')"
            )
        self.base_query = query
        self.filters    = []
        self.params     = []

    def add_filter(self, column, operator, value):
        self.filters.append((column, operator))
        self.params.append(value)

    def clear_filters(self):
        self.filters = []
        self.params  = []

    def fetch(self):
        sql    = self.build_sql()
        cursor = self.conn.execute(sql, self.params)
        cols   = [desc[0] for desc in cursor.description]
        rows   = [list(row) for row in cursor.fetchall()]
        return (cols, rows)

    def build_sql(self):
        if not self.filters:
            return self.base_query
        clauses = [f"{col} {op} ?" for col, op in self.filters]
        where   = " AND ".join(clauses)
        return f"SELECT * FROM ({self.base_query}) AS _ipui WHERE {where}"

    def close(self):
        if self.owns_conn and self.conn:
            self.conn.close()
            self.conn = None