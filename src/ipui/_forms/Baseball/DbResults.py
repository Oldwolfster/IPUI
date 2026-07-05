
from pathlib import Path
import sqlite3



class DbResults:
    """Append-only run history. Its own DB file — Phoenix never touches it, nothing here is ever deleted."""

    DB_PATH = str(Path.home() / ".neuroforge" / "projects" / "dbResults.db")
    # DbResults.py  class attr: COLS  Update: full replacement
    COLS = ("run_id", "GD", "seed", "model_name", "target_field", "run_mae", "mae", "label",
            "train_rows", "predictions", "predicted_total", "actual_total", "feature_count",
            "forest_table", "predict_table", "grain",
            "train_start_gd", "train_end_gd", "hyper", "features_csv", "created_ds")

    # DbResults.py  class attr: SCHEMA  Update: full replacement
    SCHEMA = """
        CREATE TABLE IF NOT EXISTS run_gd (
            run_id          INTEGER,
            GD              INTEGER,
            seed            INTEGER,
            model_name      TEXT,
            target_field    TEXT,
            run_mae         REAL,
            mae             REAL,
            label           TEXT,
            train_rows      INTEGER,
            predictions     INTEGER,
            predicted_total REAL,
            actual_total    REAL,
            feature_count   INTEGER,
            forest_table    TEXT,
            predict_table   TEXT,
            grain           TEXT,
            train_start_gd  INTEGER,
            train_end_gd    INTEGER,
            hyper           TEXT,
            features_csv    TEXT,
            created_ds      TEXT,
            PRIMARY KEY (run_id, GD, model_name)
        ) WITHOUT ROWID
    """



    # DbResults.py  method: update_run_mae  NEW: prediction-weighted pooled MAE, stamped on every row of the run
    @classmethod
    def update_run_mae(cls, run_id):
        conn = cls.open_conn()
        val  = conn.execute("SELECT SUM(mae * predictions) / SUM(predictions) FROM run_gd WHERE run_id = ?", (run_id,)).fetchone()[0]
        conn.execute("UPDATE run_gd SET run_mae = ? WHERE run_id = ?", (val, run_id))
        conn.commit()
        conn.close()
        return val

    @classmethod
    def open_conn(cls):
        conn = sqlite3.connect(cls.DB_PATH)
        conn.execute(cls.SCHEMA)
        return conn

    @classmethod
    def next_run_id(cls):
        conn = cls.open_conn()
        val  = conn.execute("SELECT COALESCE(MAX(run_id), 0) + 1 FROM run_gd").fetchone()[0]
        conn.close()
        return val

    @classmethod
    def insert_run_gd(cls, row):
        sql  = f"INSERT INTO run_gd ({', '.join(cls.COLS)}) VALUES ({', '.join('?' * len(cls.COLS))})"
        conn = cls.open_conn()
        conn.execute(sql, tuple(row[c] for c in cls.COLS))
        conn.commit()
        conn.close()

