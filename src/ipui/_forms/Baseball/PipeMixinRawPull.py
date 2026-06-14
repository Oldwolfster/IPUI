import time as _time
import pybaseball
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrDT import MgrDT


class MixinRawPull:

    # ══════════════════════════════════════════════════════════════
    # RAW PITCHES — pybaseball.statcast, one day at a time
    # ══════════════════════════════════════════════════════════════

    def sync_raw_pitches(self, gd):
        BbDB.log("raw_pitches", f"pull starting: GD= {gd}")
        t_overall  = _time.time()
        total_rows = 0
        known_cols = self.known_raw_pitches_cols()

        #for gd_int in MgrDT.gd_range(start_gd, end_gd):
        day_str = MgrDT.gd_to_iso(gd)
        t_day   = _time.time()
        try:
            df = pybaseball.statcast(start_dt=day_str, end_dt=day_str, verbose=False)
        except Exception as e:
            BbDB.log("raw_pitches", f"{day_str} statcast call failed: {e}")


        if df is None or len(df) == 0:
            BbDB.log("raw_pitches", f"{day_str} returned 0 rows (off day?)")
            return

        df = self.conform_pitches_df(df, gd, known_cols)
        n  = self.replace_day_pitches(gd, df)
        ms = int((_time.time() - t_day) * 1000)
        BbDB.log("raw_pitches", f"{day_str} inserted {n} rows ({ms}ms)")
        total_rows += n

        ms_total = int((_time.time() - t_overall) * 1000)
        BbDB.log("raw_pitches", f"pull complete: {total_rows} rows ({ms_total}ms)")

    def conform_pitches_df(self, df, gd_int, known_cols):
        df['GD'] = gd_int
        if 'game_date' in df.columns:
            df = df.drop(columns=['game_date'])
        extras  = set(df.columns) - known_cols
        missing = known_cols - set(df.columns)
        if extras:
            BbDB.log("raw_pitches", f"Statcast drift — dropping: {sorted(extras)}")
        if missing:
            BbDB.log("raw_pitches", f"expected cols missing: {sorted(missing)}")
        keep = [c for c in df.columns if c in known_cols]
        return df[keep]

    def replace_day_pitches(self, gd_int, df):
        import sqlite3
        conn = sqlite3.connect(BbDB.DB_PATH)
        cur  = conn.execute("DELETE FROM raw_pitches WHERE GD = ?", (gd_int,))
        if cur.rowcount > 0:
            BbDB.log("raw_pitches", f"GD {gd_int} replaced {cur.rowcount} existing rows")
        df.to_sql("raw_pitches", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()
        return len(df)

    def known_raw_pitches_cols(self):
        rows = BbDB.query("PRAGMA table_info(raw_pitches)")
        return set(r[1] for r in rows)

    # ══════════════════════════════════════════════════════════════
    # RAW TEAMS — statsapi, snapshot with today's GD
    # ══════════════════════════════════════════════════════════════

    def sync_raw_teams(self, start_gd):
        import statsapi
        BbDB.log("raw_teams", "pulling teams")
        gd    = MgrDT.today_gd()
        teams = statsapi.get('teams', {'sportId': 1})['teams']
        rows  = 0
        for t in teams:
            if not t.get('active'):                                      continue
            BbDB.execute("""
                INSERT INTO raw_teams (GD, team_id, team_name, abbreviation, location_name, league, division)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(GD, team_id) DO UPDATE SET
                    team_name     = excluded.team_name,
                    abbreviation  = excluded.abbreviation,
                    location_name = excluded.location_name,
                    league        = excluded.league,
                    division      = excluded.division
            """, (
                gd,
                t['id'],
                t['name'],
                t.get('abbreviation', ''),
                t.get('locationName', ''),
                t.get('league', {}).get('name', ''),
                t.get('division', {}).get('name', ''),
            ))
            rows += 1
        BbDB.log("raw_teams", f"loaded {rows} teams")

    # ══════════════════════════════════════════════════════════════
    # RAW PLAYERS — statsapi, IDs from raw_pitches (not etl_pa!)
    # ══════════════════════════════════════════════════════════════

    def sync_raw_players(self, start_gd):
        import statsapi
        BbDB.log("raw_players", "pulling players")
        gd  = MgrDT.today_gd()
        ids = [r[0] for r in BbDB.query("""
            SELECT DISTINCT batter  FROM raw_pitches
            UNION
            SELECT DISTINCT pitcher FROM raw_pitches
        """)]
        BbDB.log("raw_players", f"found {len(ids)} unique player IDs")
        rows = 0
        for i in range(0, len(ids), 100):
            batch  = ids[i:i + 100]
            id_str = ",".join(str(x) for x in batch)
            people = statsapi.get('people', {'personIds': id_str, 'hydrate': 'currentTeam'})['people']
            for p in people:
                BbDB.execute("""
                    INSERT INTO raw_players
                        (GD, player_id, full_name, use_name, boxscore_name,
                         position, bat_side, throw_hand, team_id, jersey_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(GD, player_id) DO UPDATE SET
                        full_name     = excluded.full_name,
                        use_name      = excluded.use_name,
                        boxscore_name = excluded.boxscore_name,
                        position      = excluded.position,
                        bat_side      = excluded.bat_side,
                        throw_hand    = excluded.throw_hand,
                        team_id       = excluded.team_id,
                        jersey_number = excluded.jersey_number
                """, (
                    gd,
                    p['id'],
                    p.get('fullName', ''),
                    p.get('useName', ''),
                    p.get('boxscoreName', ''),
                    p.get('primaryPosition', {}).get('abbreviation', ''),
                    p.get('batSide', {}).get('code', ''),
                    p.get('pitchHand', {}).get('code', ''),
                    p.get('currentTeam', {}).get('id'),
                    p.get('primaryNumber', ''),
                ))
                rows += 1
        BbDB.log("raw_players", f"loaded {rows} players")