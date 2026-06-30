# MgrSqlBeautification.py  NEW FILE (CSR)

class MgrSqlBeautification:
    GUTTER      = 11
    COMPOUND_KW = ['LEFT OUTER JOIN', 'RIGHT OUTER JOIN',
                   'LEFT JOIN',  'RIGHT JOIN', 'INNER JOIN',
                   'OUTER JOIN', 'CROSS JOIN', 'GROUP BY',
                   'ORDER BY',  'INSERT INTO', 'CREATE VIEW']
    SINGLE_KW   = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'ON',
                   'JOIN', 'HAVING', 'LIMIT', 'UNION', 'SET',
                   'WITH', 'UPDATE', 'DELETE']
    SPACING_KW  = {'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN',
                   'INNER JOIN', 'CROSS JOIN', 'LEFT OUTER JOIN',
                   'RIGHT OUTER JOIN', 'OUTER JOIN',
                   'GROUP BY', 'ORDER BY', 'HAVING', 'UNION', 'WITH'}

    # ══════════════════════════════════════════════════════════════
    # ORCHESTRATOR — no logic, just calls
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def format_sql(sql, line_feed='\n'):
        sql = MgrSqlBeautification.normalize_whitespace(sql, line_feed)
        sql = MgrSqlBeautification.keyword_uppercase(sql)
        sql = MgrSqlBeautification.comma_comelyfication(sql, line_feed)
        sql = MgrSqlBeautification.format_block(sql, line_feed)
        sql = MgrSqlBeautification.align_equals(sql, line_feed)
        sql = MgrSqlBeautification.clause_spacing(sql, line_feed)
        return sql

    # ══════════════════════════════════════════════════════════════
    # PHASE 1 — normalize whitespace
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def normalize_whitespace(sql, line_feed):
        lines        = sql.split(line_feed)
        lines        = [line.rstrip()          for line in lines]
        lines        = [line for i, line
                        in enumerate(lines)
                        if line.strip() or (i > 0 and lines[i-1].strip())]
        while lines and not lines[0].strip():  lines.pop(0)
        while lines and not lines[-1].strip(): lines.pop()
        return line_feed.join(lines)

    # ══════════════════════════════════════════════════════════════
    # PHASE 2 — uppercase keywords
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def keyword_uppercase(sql):
        import re
        keywords = [
            'select', 'from', 'where', 'and', 'or', 'not',
            'join', 'left', 'right', 'inner', 'outer', 'cross', 'full',
            'on', 'as', 'in', 'is', 'null', 'by', 'group', 'order',
            'having', 'limit', 'offset', 'distinct', 'case', 'when',
            'then', 'else', 'end', 'insert', 'into', 'update', 'set',
            'delete', 'create', 'view', 'with', 'union', 'all', 'exists',
            'between', 'like', 'nullif', 'coalesce', 'sum', 'count',
            'min', 'max', 'avg', 'round', 'cast', 'over', 'partition',
        ]
        pattern = r'\b(' + '|'.join(keywords) + r')\b'
        return re.sub(pattern, lambda m: m.group().upper(), sql, flags=re.IGNORECASE)

    # ══════════════════════════════════════════════════════════════
    # PHASE 3 — leading commas
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def comma_comelyfication(sql, line_feed):
        lines  = sql.split(line_feed)
        result = []
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped.endswith(',') and i + 1 < len(lines):
                next_line    = lines[i + 1]
                indent       = len(next_line) - len(next_line.lstrip())
                result.append(stripped[:-1])
                lines[i + 1] = ' ' * indent + ',' + next_line.lstrip()
            else:
                result.append(stripped)
        return line_feed.join(result)

    # ══════════════════════════════════════════════════════════════
    # PHASE 4 — keyword gutter + recursive subqueries
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def format_block(sql, line_feed='\n', base=0):
        lines = sql.split(line_feed)
        out   = MgrSqlBeautification.format_lines(lines, base, line_feed)
        return line_feed.join(out)

    @staticmethod
    def format_lines(lines, base, line_feed):
        ME     = MgrSqlBeautification
        G      = ME.GUTTER
        result = []
        i      = 0
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped:
                result.append('')
                i += 1
                continue
            if stripped.startswith('--'):
                result.append(' ' * base + stripped)
                i += 1
                continue
            kw, content = ME.extract_keyword(stripped)
            if content.rstrip().endswith('(') and ME.is_subquery(lines, i + 1):
                next_i, sub_lines = ME.format_subquery(lines, i, kw, content, base, line_feed)
                result.extend(sub_lines)
                i = next_i
                continue
            if kw:
                result.append(ME.gutter_line(kw, content, base))
            else:
                result.append(' ' * (base + G) + stripped)
            i += 1
        return result

    @staticmethod
    def extract_keyword(stripped):
        ME    = MgrSqlBeautification
        upper = stripped.upper()
        for kw in sorted(ME.COMPOUND_KW, key=len, reverse=True):
            if upper.startswith(kw):
                rest = stripped[len(kw):]
                if not rest or rest[0] in ' \t(':
                    return kw, rest.strip()
        for kw in ME.SINGLE_KW:
            if upper.startswith(kw):
                rest = stripped[len(kw):]
                if not rest or rest[0] in ' \t(':
                    return kw, rest.strip()
        return None, stripped

    @staticmethod
    def gutter_line(kw, content, base):
        G = MgrSqlBeautification.GUTTER
        if kw:
            return ' ' * base + kw.ljust(G) + content
        return ' ' * (base + G) + content

    @staticmethod
    def is_subquery(lines, start):
        ME = MgrSqlBeautification
        for j in range(start, len(lines)):
            stripped = lines[j].strip()
            if stripped:
                kw, _ = ME.extract_keyword(stripped)
                return kw == 'SELECT'
        return False

    @staticmethod
    def collect_subquery(lines, start):
        depth = 1
        inner = []
        for i in range(start, len(lines)):
            stripped = lines[i].strip()
            depth   += stripped.count('(') - stripped.count(')')
            if depth <= 0:
                return inner, i
            inner.append(stripped)
        return inner, len(lines) - 1

    @staticmethod
    def format_subquery(lines, i, kw, content, base, line_feed):
        ME           = MgrSqlBeautification
        G            = ME.GUTTER
        result       = []
        open_content = content.rstrip()[:-1].strip()
        open_part    = '(' if not open_content else open_content + ' ('
        result.append(ME.gutter_line(kw, open_part, base))
        inner, close_i = ME.collect_subquery(lines, i + 1)
        inner_sql      = line_feed.join(inner)
        inner_fmt      = ME.format_block(inner_sql, line_feed, base + G)
        result.extend(inner_fmt.split(line_feed))
        close_stripped  = lines[close_i].strip() if close_i < len(lines) else ')'
        result.append(ME.gutter_line(None, close_stripped, base))
        return close_i + 1, result

    # ══════════════════════════════════════════════════════════════
    # PHASE 5 — align = within each clause group
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def align_equals(sql, line_feed='\n'):
        ME     = MgrSqlBeautification
        lines  = sql.split(line_feed)
        groups = ME.group_by_indent(lines)
        result = []
        for group in groups:
            result.extend(ME.align_equals_in_group(group))
        return line_feed.join(result)

    @staticmethod
    def group_for_equalsDeleteMe(lines):
        ME      = MgrSqlBeautification
        groups  = []
        current = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current: groups.append(current)
                current = []
                groups.append([line])
                continue
            kw, _ = ME.extract_keyword(stripped)
            if kw in ME.SPACING_KW and current:
                groups.append(current)
                current = [line]
            else:
                current.append(line)
        if current:
            groups.append(current)
        return groups

    @staticmethod
    def group_by_indent(lines):
        groups = []
        current = []
        prev_indent = -1
        for line in lines:
            if not line.strip():
                if current: groups.append(current)
                current = []
                groups.append([line])
                prev_indent = -1
                continue
            indent = len(line) - len(line.lstrip())
            if indent != prev_indent and current:
                groups.append(current)
                current = [line]
            else:
                current.append(line)
            prev_indent = indent
        if current:
            groups.append(current)
        return groups
    @staticmethod
    def align_equals_in_group(group):
        eq_lines = [l for l in group if ' = ' in l and not l.strip().startswith('--')]
        if len(eq_lines) < 2:
            return group
        max_pos = max(l.index(' = ') for l in eq_lines)
        result  = []
        for line in group:
            if ' = ' in line and not line.strip().startswith('--'):
                pos    = line.index(' = ')
                before = line[:pos]
                after  = line[pos + 3:]
                line   = before + ' ' * (max_pos - pos) + ' = ' + after
            result.append(line)
        return result

    # ══════════════════════════════════════════════════════════════
    # PHASE 6 — blank line between major clauses
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def clause_spacing(sql, line_feed='\n'):
        ME     = MgrSqlBeautification
        lines  = sql.split(line_feed)
        result = []
        for i, line in enumerate(lines):
            kw, _ = ME.extract_keyword(line.strip())
            if kw in ME.SPACING_KW and i > 0 and result and result[-1].strip():
                result.append('')
            result.append(line)
        return line_feed.join(result)


