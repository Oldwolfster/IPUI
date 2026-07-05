# MgrDT.py  class: MgrDT  NEW: ipui core date utility — GD int (YYYYMMDD) as universal date format

import datetime as _dt

from ipui.utils.EZ import EZ


class MgrDT:

    # ─── format constants ──────────────────────────────────────
    FMT_GD       = "%Y%m%d"                                  # 20260715
    FMT_ISO      = "%Y-%m-%d"                                # 2026-07-15  (user-facing default)
    FMT_LOG      = "%Y-%m-%d %H:%M:%S"                       # 2026-07-15 14:23:11
    FMT_COMPACT  = "%b %d"                                   # Jul 15

    GD_CAREER    = 999999                                    # sentinel: career-to-date
    GD_SEASON    = 200                                       # sentinel: current season-to-date (in TS context)


    # ══════════════════════════════════════════════════════════════
    # CREATION
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def today_gd(cls):
        return int(_dt.date.today().strftime(cls.FMT_GD))

    @classmethod
    def today_ds(cls):
        return _dt.datetime.now().strftime(cls.FMT_LOG)

    @classmethod
    def today_iso(cls):
        return _dt.date.today().strftime(cls.FMT_ISO)


    # ══════════════════════════════════════════════════════════════
    # CONVERSIONS — scalar only. DataFrame-column operations belong
    # at their source (e.g. Statcast conform_pitches_df).
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def gd_to_date(cls, gd_int):
        s = str(gd_int)
        return _dt.date(int(s[0:4]), int(s[4:6]), int(s[6:8]))

    @classmethod
    def date_to_gd(cls, d):
        return int(d.strftime(cls.FMT_GD))

    @classmethod
    def gd_to_iso(cls, gd_int):
        if gd_int is None:                                   # graceful for empty tables
            return "—"
        return cls.gd_to_date(gd_int).strftime(cls.FMT_ISO)

    @classmethod
    def gd_to_compact(cls, gd_int):
        if gd_int is None:
            return "—"
        return cls.gd_to_date(gd_int).strftime(cls.FMT_COMPACT)

    @classmethod
    def iso_to_gd(cls, s):
        return int(s.replace('-', ''))

    @classmethod
    def str_to_gdOLD(cls, s):                                   # tolerant: accepts -, /, or no separator
        return int(s.strip().replace('-', '').replace('/', ''))

    @classmethod
    def str_to_gd(cls, s, blank_is_today=True):
        s = (s or "").strip()
        if not s:
            if blank_is_today:  return cls.today_gd()
            EZ.err("Blank date. Expected: 20260704, 2026-7-4, 7/4/2026, or 7/4")
        for sep in ('/', '.', ' '):  s = s.replace(sep, '-')
        if '-' in s:  return cls.gd_from_parts(s.split('-'))
        return cls.gd_from_digits(s)
    # ══════════════════════════════════════════════════════════════
    # MATH
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def gd_add_days(cls, gd_int, n):
        return cls.date_to_gd(cls.gd_to_date(gd_int) + _dt.timedelta(days=n))

    @classmethod
    def gd_minus_days(cls, gd_expr, days):
        return cls.gd_add_days(gd_expr, days+1)

    # TODO GET THE ABOVE WORKING
    @classmethod
    def gd_minus_days(cls, gd_expr, days):
        iso = (f"substr(cast({gd_expr} as text),1,4)||'-'||"
               f"substr(cast({gd_expr} as text),5,2)||'-'||"
               f"substr(cast({gd_expr} as text),7,2)")
        return f"cast(replace(date({iso}, '-{days} days'), '-', '') as integer)"

    @classmethod
    def gd_diff_days(cls, gd_a, gd_b):
        return (cls.gd_to_date(gd_a) - cls.gd_to_date(gd_b)).days

    @classmethod
    def gd_range(cls, start_gd, end_gd):                     # generator: yields each GD in [start, end] inclusive
        d   = cls.gd_to_date(start_gd)
        end = cls.gd_to_date(end_gd)
        while d <= end:
            yield cls.date_to_gd(d)
            d += _dt.timedelta(days=1)


    # ══════════════════════════════════════════════════════════════
    # VALIDATION
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def is_valid_gd(cls, gd_int):
        try:
            cls.gd_to_date(gd_int)
            return True
        except (ValueError, IndexError, TypeError):
            return False

        # MgrDT.py method: gd_from_parts  NEW: separator path — year is wherever the 4-digit part is
    @classmethod
    def gd_from_parts(cls, parts):
        parts = [p for p in parts if p]                       # tolerate doubled separators
        if len(parts) == 2:    return cls.gd_validate(cls.today_gd() // 10000, parts[0], parts[1])
        if len(parts) != 3:    EZ.err(f"Can't parse date parts {parts}. Expected Y-M-D, M/D/Y, or M/D")
        if len(parts[0]) == 4: return cls.gd_validate(parts[0], parts[1], parts[2])
        if len(parts[2]) == 4: return cls.gd_validate(parts[2], parts[0], parts[1])
        EZ.err(f"No 4-digit year in {parts}. Expected Y-M-D, M/D/Y, or M/D")

    # MgrDT.py method: gd_from_digits  NEW: bare-digit path — 8 only; 6/7 rejected as ambiguous
    @classmethod
    def gd_from_digits(cls, s):
        if len(s) == 8 and s.isdigit():  return cls.gd_validate(s[:4], s[4:6], s[6:8])
        if len(s) in (6, 7) and s.isdigit():
            EZ.err(f"'{s}' is ambiguous — e.g. 2026112 could be Jan 12 or Nov 2.\nUse 8 digits (20260704) or separators (2026-7-4)")
        EZ.err(f"Can't parse date '{s}'. Expected: 20260704, 2026-7-4, 7/4/2026, or 7/4")

    # MgrDT.py method: gd_validate  NEW: real calendar check (kills 20261399, respects leap years)
    @classmethod
    def gd_validate(cls, y, m, d):
        try:                return cls.date_to_gd(_dt.date(int(y), int(m), int(d)))
        except ValueError:  EZ.err(f"Not a real calendar date: year={y} month={m} day={d}")
