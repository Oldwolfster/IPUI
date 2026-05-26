from ipui import *
from ipui._forms.Baseball.BB_Schema import BB_Schema
from ipui.widgets.Label import Detail
from datetime import date, timedelta, datetime
from pybaseball import statcast

from ipui import *
import sqlite3
from pathlib import Path
from datetime import datetime



class Pipe(_BaseTab):

    DB_PATH = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")

    SYNC_DEPS = {
        "staging_batter_features_season":      ["plate_appearances"],
        "staging_batter_features_recent_form": ["batter_games"],            # NEW
        "batter_features":                     ["staging_batter_features_season",
                                                "staging_batter_features_recent_form"],  # UPDATED
        "pitcher_features":                    ["plate_appearances"],
        "batter_games":                        ["plate_appearances"],
        "league_summary":                      ["plate_appearances"],
        "pitcher_pitch_mix":                   ["pitch_bucketed"],
        "batter_vs_pitch":                     ["pitch_bucketed"],
    }

    EVENT_BASES = {
        "single"  : 1,
        "double"  : 2,
        "triple"  : 3,
        "home_run": 4,
    }

    PITCH_BUCKETS = {
        "FF": "fastball", "SI": "fastball", "FC": "fastball", "FA": "fastball",
        "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking", "SV": "breaking", "CS": "breaking",
        "CH": "offspeed", "FS": "offspeed", "SP": "offspeed", "FO": "offspeed",
    }
    BUCKETS = ["fastball", "breaking", "offspeed", "other"]
    # ══════════════════════════════════════════════════════════════
    # IMPERATIVE — manual wiring
    # ══════════════════════════════════════════════════════════════

    def all_in_one(self, parent):
        print("all  in one")#
        BB_Schema.bootstrap(self.DB_PATH)
        #pitches_min, pitches_max = self.get_dates("pitches")

        frame = CardCol(parent, flex_height=1)
        header = Row(frame)
        Title(header, "ETL Pipeline", glow=True)
        Button(header, "Build Indexes",color_bg=Style.COLOR_BUTTON_CTA,on_click=self.passme)
        Button(header, "Harvest Batters", on_click=self.passme)
        Button(header, "Sync Schedule", on_click=self.passme)
        Spacer(header)
        Button(header, "Nuke", on_click=self.passme,color_bg=Style.COLOR_BUTTON_DANGER)
        #self.build_pitches_plate(frame, pitches_min, pitches_max)

    def passme(self):
        pass