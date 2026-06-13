class MgrSqlBeautification :


    @staticmethod
    def format_sql(sql, line_feed='\n'):
        sql = MgrSqlBeautification.normalize_whitespace(sql, line_feed)
        sql = MgrSqlBeautification.keyword_uppercase(sql)
        sql = MgrSqlBeautification.comma_comelyfication(sql, line_feed)
        sql = MgrSqlBeautification.align_columns(sql)
        #sql = MgrSqlBeautification.align_conditions(sql)
        sql = MgrSqlBeautification.indent_subqueries(sql)
        return sql


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

    @staticmethod
    def keyword_uppercase(sql):
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
        import re
        pattern = r'\b(' + '|'.join(keywords) + r')\b'
        return re.sub(pattern, lambda m: m.group().upper(), sql, flags=re.IGNORECASE)




    @staticmethod
    def comma_comelyfication(sql, line_feed):
        lines  = sql.split(line_feed)
        result = []
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped.endswith(',') and i + 1 < len(lines):
                next_line         = lines[i + 1]
                indent            = len(next_line) - len(next_line.lstrip())
                result.append(stripped[:-1])
                lines[i + 1]      = ' ' * indent + ',' + next_line.lstrip()
            else:
                result.append(stripped)
        return line_feed.join(result)




    @staticmethod
    def align_columns(sql, line_feed='\n'):
        import re
        lines = sql.split(line_feed)
        clauses = []
        current = []
        keywords = {'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT',
                    'INNER', 'OUTER', 'ON', 'GROUP', 'ORDER', 'HAVING'}
        for line in lines:
            first_word = line.strip().split()[0].upper() if line.strip() else ''
            if first_word in keywords and current:
                clauses.append(current)
                current = [line]
            else:
                current.append(line)
        if current:
            clauses.append(current)

        result = []
        for clause in clauses:
            as_lines = [l for l in clause if re.search(r'\bAS\b', l, re.IGNORECASE)]
            if len(as_lines) < 2:
                result.extend(clause)
                continue
            max_len = max(
                len(line[:re.search(r'\bAS\b', line, re.IGNORECASE).start()].rstrip()) for line in as_lines)
            target = max_len + 2
            for line in clause:
                match = re.search(r'\bAS\b', line, re.IGNORECASE)
                if match:
                    before = line[:match.start()].rstrip()
                    after = line[match.end():]
                    line = before + ' ' * (target - len(before)) + 'AS' + after
                result.append(line)
        return line_feed.join(result)

    @staticmethod
    def align_conditions(self, sql):
        return sql


    # MgrSqlBeautification.py  method: indent_subqueries  UPDATE: dispatcher only
    @staticmethod
    def indent_subqueries(sql, line_feed='\n', spaces=4):
        lines  = sql.split(line_feed)
        state  = MgrSqlBeautification.build_indent_state(lines, spaces)
        return line_feed.join(MgrSqlBeautification.apply_indent(line, depth) for line, depth in zip(lines, state))

    # MgrSqlBeautification.py  method: build_indent_state  NEW: returns list of indent per line
    @staticmethod
    def build_indent_state(lines, spaces):
        import re
        keywords    = {'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT',
                       'INNER', 'OUTER', 'CROSS', 'ON', 'GROUP', 'ORDER',
                       'HAVING', 'UNION'}
        result      = []
        select_cnt  = 0
        sub_depth   = 0
        paren_depth = 0
        paren_stack = []
        for line in lines:
            stripped    = line.strip()
            if not stripped:
                result.append(0)
                continue
            paren_depth += stripped.count('(') - stripped.count(')')
            first_word   = re.match(r'\w+', stripped)
            first_word   = first_word.group().upper() if first_word else ''
            if first_word == 'SELECT':
                select_cnt += 1
                if select_cnt > 1:
                    sub_depth += 1
                    paren_stack.append(paren_depth)
            while paren_stack and paren_depth < paren_stack[-1]:
                paren_stack.pop()
                sub_depth -= 1
            base   = sub_depth   * spaces
            indent = base if first_word in keywords else base + spaces
            result.append(indent)
        return result

    # MgrSqlBeautification.py  method: apply_indent  NEW: strips and re-pads one line
    @staticmethod
    def apply_indent(line, indent):
        stripped = line.strip()
        if not stripped: return ''
        return ' ' * indent + stripped