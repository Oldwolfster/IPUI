# FieldLineage.py  NEW FILE
import re
from collections import namedtuple

from ipui._forms.Baseball.BbDB import BbDB

Hop = namedtuple('Hop', ['table', 'field', 'field_exists', 'depth'])


class FieldLineage:
    """Stateless field-lineage tracer. Given (field, table), traces
       backward to raw sources and forward to all downstream consumers."""

    # ══════════════════════════════════════════════════════════════
    # PUBLIC — single entry point
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def trace(field, table):
        backward = FieldLineage.trace_backward(field, table, depth=0)
        forward  = FieldLineage.trace_forward(field, table, depth=0)
        return backward, forward

    # ══════════════════════════════════════════════════════════════
    # BACKWARD — heritage: where did this field come from?
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def trace_backward(field, table, depth, visited=None):
        if visited is None: visited = set()
        if table in visited: return []
        visited.add(table)
        hops    = []
        view_sql = FieldLineage.pull_view_sql(table)
        if view_sql is None:
            return [Hop(table, field, FieldLineage.table_has_field(table, field), depth)]
        source_field, source_table = FieldLineage.resolve_field_source(field, view_sql)
        if source_table is None:
            sources = FieldLineage.parse_sources(view_sql)
            for src in sources:
                exists = FieldLineage.table_has_field(src, field)
                if exists:
                    hops.append(Hop(src, field, True, depth + 1))
                    hops.extend(FieldLineage.trace_backward(field, src, depth + 2, visited))
                    return hops
            if sources:
                hops.append(Hop(sources[0], field, False, depth + 1))
            return hops
        hops.append(Hop(source_table, source_field, FieldLineage.table_has_field(source_table, source_field), depth + 1))
        hops.extend(FieldLineage.trace_backward(source_field, source_table, depth + 2, visited))
        return hops

    # ══════════════════════════════════════════════════════════════
    # FORWARD — lineage: who consumes this field?
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def trace_forward(field, table, depth, visited=None):
        if visited is None: visited = set()
        if table in visited: return []
        visited.add(table)
        hops      = []
        consumers = FieldLineage.consumer_tables(table)
        for dest in consumers:
            dest_field = FieldLineage.resolve_field_alias(field, table, dest)
            exists     = FieldLineage.table_has_field(dest, dest_field)
            hops.append(Hop(dest, dest_field, exists, depth + 1))
            hops.extend(FieldLineage.trace_forward(dest_field, dest, depth + 2, visited))
        return hops

    # ══════════════════════════════════════════════════════════════
    # SQL PARSING — extract sources and field mappings
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def pull_view_sql(table):
        pull_name = f"pull_{table}"
        rows = BbDB.query("SELECT sql FROM sqlite_master WHERE type='view' AND name = ?", (pull_name,))
        if not rows or rows[0][0] is None: return None
        return rows[0][0]

    @staticmethod
    def parse_sources(sql):
        pattern = r'(?:FROM|JOIN)\s+(\w+)'
        return list(dict.fromkeys(re.findall(pattern, sql, re.IGNORECASE)))

    @staticmethod
    def resolve_field_source(field, view_sql):
        """Given a destination field name and a pull view's SQL,
           find which source_table.source_field it came from."""
        select_block = FieldLineage.extract_select_block(view_sql)
        for expr in FieldLineage.split_select_exprs(select_block):
            src, alias = FieldLineage.parse_select_expr(expr)
            if alias == field and src:
                parts = src.rsplit('.', 1)
                if len(parts) == 2:
                    return parts[1], FieldLineage.resolve_source_to_table(parts[0], view_sql)
                return src, None
        return field, None

    @staticmethod
    def resolve_field_alias(field, source_table, dest_table):
        """Given field in source_table, find what it's aliased to in dest's pull view."""
        view_sql = FieldLineage.pull_view_sql(dest_table)
        if view_sql is None: return field
        select_block = FieldLineage.extract_select_block(view_sql)
        for expr in FieldLineage.split_select_exprs(select_block):
            src, alias = FieldLineage.parse_select_expr(expr)
            if src and source_table in src and src.rsplit('.', 1)[-1] == field:
                return alias if alias else field
        return field

    @staticmethod
    def resolve_source_to_table(ref, view_sql):
        """Given a table/view reference from a SELECT column, find the real table.
           If it's a mixin view, follow to its FROM source."""
        if ref.startswith('pull_'):
            mixin_sql = BbDB.query("SELECT sql FROM sqlite_master WHERE type='view' AND name = ?", (ref,))
            if mixin_sql and mixin_sql[0][0]:
                sources = FieldLineage.parse_sources(mixin_sql[0][0])
                return sources[0] if sources else ref
        return ref

    # ══════════════════════════════════════════════════════════════
    # SELECT BLOCK PARSING — split and interpret expressions
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def extract_select_block(sql):
        match = re.search(r'\bSELECT\b(.*?)\bFROM\b', sql, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ''

    @staticmethod
    def split_select_exprs(block):
        return [e.strip() for e in block.split(',') if e.strip()]

    @staticmethod
    def parse_select_expr(expr):
        """Returns (source_ref, alias) from a SELECT expression.
           Handles: table.col alias, table.col AS alias, table.col"""
        expr = expr.strip()
        as_match = re.match(r'(.+?)\s+AS\s+(\w+)\s*$', expr, re.IGNORECASE)
        if as_match:
            return as_match.group(1).strip(), as_match.group(2)
        parts = expr.split()
        if len(parts) == 2 and '(' not in parts[0]:
            return parts[0], parts[1]
        if len(parts) == 1:
            col = parts[0].rsplit('.', 1)[-1]
            return parts[0], col
        return expr, None

    # ══════════════════════════════════════════════════════════════
    # SCHEMA QUERIES — field existence
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def table_has_field(table, field):
        cols = BbDB.query(f"PRAGMA table_info({table})")
        return any(c[1] == field for c in cols)

    @staticmethod
    def consumer_tables(table):
        """Find all tables whose pull view references this table in FROM/JOIN."""
        views = BbDB.query("SELECT name, sql FROM sqlite_master WHERE type='view' AND name LIKE 'pull_%'")
        result = []
        for name, sql in views:
            if sql and re.search(r'(?:FROM|JOIN)\s+' + re.escape(table) + r'\b', sql, re.IGNORECASE):
                dest = name.replace('pull_', '', 1)
                if dest != table:
                    result.append(dest)
        return result