import os
import uuid
import json
import multiprocessing
import subprocess

from ipui.docs.ProjectManager import ProjectManager


#TODO rename frm is confusing as other frm are all tabs.
class SubProcesses:

    MAX_SHARDS = min(multiprocessing.cpu_count() - 1, 8)

    @staticmethod
    def write_launch_config(form):
        import sqlite3
        guid, config_json = SubProcesses.build_launch_config(form)
        db_path = form.active_project.path

        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO launch_config (guid, config) VALUES (?, ?)",
            (guid, config_json),
        )
        conn.commit()
        conn.close()
        return guid

    @staticmethod
    def build_launch_config(form):
        gladiators   = form.pipeline_read("GladiatorList") or []
        arenas       = form.pipeline_read("ArenaList") or []
        random_count = form.pipeline_read("SeedCountRandom")
        manual_seeds = form.pipeline_read("SeedListManual") or []

        if random_count is None:
            random_count = 0 if manual_seeds else 1

        import random
        seeds = manual_seeds + [random.randint(1, 999999) for _ in range(random_count)]


        dimensions = {}  
        CONFIG_KEYS = {  
            "optimizer": "OptimizerList",  
            "hidden_activation": "HiddenActivationList",  
            "output_activation": "OutputActivationList",  
            "loss_function": "LossFunctionList",  
            "weight_initializer": "InitializerList",  
            "input_scaler": "InputScalerList",  
            "target_scaler": "TargetScalerList",  
        }  
        for dim_name, pipeline_key in CONFIG_KEYS.items():  
            vals = form.pipeline_read(pipeline_key) or []  
            if vals:  
                dimensions[dim_name] = vals

        config = {
            "gladiators":        gladiators,
            "arenas":            arenas,
            "seeds":             seeds,
            "epochs_to_run":     int(form.pipeline_read("HP_Epochs to Run") or 50),
            "training_set_size": int(form.pipeline_read("HP_Training Set Size") or 40),
            "learning_rate":     float(form.pipeline_read("HP_Learning Rate") or 0),
            "dimensions":        dimensions,
        }
        return str(uuid.uuid4()), json.dumps(config)

    @staticmethod
    def clear_temp_folder(form):

        from pathlib import Path  
        temp_dir = Path.home() / ".neuroforge" / "temp"  
        if temp_dir.exists():  
            for f in temp_dir.glob("mae_*"):  
                try:
                    f.unlink()  
                except OSError:
                    pass  

    @staticmethod
    def launch_prepare_batch(form):
        import sqlite3
        SubProcesses.clear_temp_folder(form)
        db_path = str(form.active_project.path)


        result = subprocess.run([
            ProjectManager.NNA_PYTHON, ProjectManager.NNA_MAIN,
            "--mode", "prepare_batch",
            "--db", db_path,
        ], capture_output=True, text=True, cwd=ProjectManager.NNA_ROOT,
           env={**os.environ, "PYTHONPATH": ProjectManager.NNA_ROOT})
        ProjectManager.print_if_error(result)

        conn = sqlite3.connect(db_path)
        row  = conn.execute(
            "SELECT batch_id FROM launch_config WHERE batch_id IS NOT NULL ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        conn.close()

        if row:
            return row[0]
        return None

    @staticmethod
    def launch_shards(form, batch_id):
        SubProcesses.seed_initial_grid(form)
        db_path     = str(form.active_project.path)
        form.shards = []

        for i in range(SubProcesses.MAX_SHARDS):
            proc = subprocess.Popen([
                ProjectManager.NNA_PYTHON, ProjectManager.NNA_MAIN,
                "--mode", "run_batch",
                "--db", db_path,
                "--shard", f"{i},{SubProcesses.MAX_SHARDS}",
            ], cwd=ProjectManager.NNA_ROOT,
                env={**os.environ, "PYTHONPATH": ProjectManager.NNA_ROOT})
            form.shards.append(proc)

    @staticmethod
    def seed_initial_grid(form):
        form.shard_states   = {}
        form.display_slots  = []
        form.file_positions = {}

        for run_id in sorted(form.run_details.keys()):
            rid = str(run_id)
            form.shard_states[rid] = {
                "phase":   "Loading",
                "display": "—",
                "mae":     "—",
                "history": [],
            }
            form.display_slots.append(rid)
            if len(form.display_slots) >= SubProcesses.MAX_SHARDS:
                break