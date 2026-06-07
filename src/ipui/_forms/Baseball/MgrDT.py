# MgrDT.py  class: MgrDT  NEW: ipui core date utility — GD int (YYYYMMDD) as universal date format

import datetime as _dt


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
    def str_to_gd(cls, s):                                   # tolerant: accepts -, /, or no separator
        return int(s.strip().replace('-', '').replace('/', ''))


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