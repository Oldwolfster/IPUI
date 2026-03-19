# ProjectManager.py

from pathlib import Path
from collections import namedtuple
import sqlite3
import os

ProjectInfo = namedtuple("ProjectInfo", [
    "name",  # Display name (without .nf)
    "path",  # Full Path object
    "mtime",  # Last modified timestamp
    "run_count",  # Actual runs completed
    "expected_runs",  # Total runs expected across all batches
    "batch_count",  # Number of batches
])


class ProjectManager:
    PROJECTS_FOLDER = Path.home() / ".neuroforge" / "projects"

    active_project_path = None  # Class-level state

    @classmethod
    def ensure_folder(cls):
        cls.PROJECTS_FOLDER.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_db_path(cls):
        """Returns active project path, or default if none selected."""
        if cls.active_project_path:
            return cls.active_project_path
        return cls.get_default_project()

    @classmethod
    def set_active_project(cls, path):
        """Sets the active project. Called by NeuroLab when user picks one."""
        cls.active_project_path = Path(path) if path else None

    @classmethod
    def get_default_project(cls):
        """Returns most recently modified project, or creates 'default.nf' if none exist."""
        projects = cls.list_projects()
        if projects:
            return projects[0].path
        return cls.create_project("default")

    @classmethod
    def list_projects(cls):
        """Returns list of ProjectInfo, sorted by mtime desc (most recent first)."""
        cls.ensure_folder()
        projects = []
        for path in cls.PROJECTS_FOLDER.glob("*.nf"):
            info = cls.get_project_info(path)
            if info:
                projects.append(info)
        return sorted(projects, key=lambda p: p.mtime, reverse=True)

    @classmethod
    def get_project_info(cls, path):
        """Quick scan: filesystem mtime, counts from DB."""
        try:
            mtime = os.path.getmtime(path)
            run_count, expected_runs, batch_count = cls.query_project_counts(path)
            return ProjectInfo(
                name=path.stem,
                path=path,
                mtime=mtime,
                run_count=run_count,
                expected_runs=expected_runs,
                batch_count=batch_count,
            )
        except Exception:
            return None

    @classmethod
    def query_project_counts(cls, path):
        """Opens DB briefly to get counts. Returns (run_count, expected_runs, batch_count)."""
        conn = sqlite3.connect(path)
        try:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM batch_history")
            run_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*), COALESCE(SUM(expected_runs), 0) FROM batch_specs")
            row = cur.fetchone()
            batch_count = row[0]
            expected_runs = row[1]

            return run_count, expected_runs, batch_count
        except sqlite3.OperationalError:
            return 0, 0, 0
        finally:
            conn.close()

    @classmethod
    def completion_percent(cls, info):
        """Returns 0-100 completion percentage, or None if no expected runs."""
        if info.expected_runs == 0:
            return None
        return int(info.run_count / info.expected_runs * 100)

    NNA_ROOT = r"C:\SynologyDrive\Development\PyCharm\NeuroForge"
    NNA_MAIN = r"C:\SynologyDrive\Development\PyCharm\NeuroForge\src\main.py"
    NNA_PYTHON = r"C:\SynologyDrive\Development\PyCharm\NeuroForge\.venv\Scripts\python.exe"

    @classmethod
    def create_project(cls, name):
        """Creates .nf project via NNA subprocess. Returns path."""
        import subprocess
        import sys

        cls.ensure_folder()
        safe_name = cls.sanitize_filename(name)
        path = cls.PROJECTS_FOLDER / f"{safe_name}.nf"

        if path.exists():
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
            safe_name = f"{safe_name}_{timestamp}"
            path = cls.PROJECTS_FOLDER / f"{safe_name}.nf"
        print(f"Creating project at: {path}")
        result = subprocess.run([
            cls.NNA_PYTHON, cls.NNA_MAIN,
            "--mode", "create_db",
            "--db", str(path),
        ], capture_output=True, text=True, cwd=cls.NNA_ROOT,
            env={**os.environ, "PYTHONPATH": cls.NNA_ROOT})
        ProjectManager.print_if_error(result)


        return path


    @classmethod
    def print_if_error(cls, result):
        if result.returncode != 0:
            #print(f" {result.stderr}")
            print(f"NNA stdout: {result.stdout}")
            raise RuntimeError(f"NNA stderr: {result.stderr}")

    @classmethod
    def sanitize_filename(cls, name):
        """Convert spaces to underscores, remove unsafe chars."""
        unsafe = '<>:"/\\|?*'
        result = name.strip()
        for char in unsafe:
            result = result.replace(char, '_')
        result = result.replace(' ', '_')  # spaces to underscores
        return result or "untitled"

    @classmethod
    def delete_project(cls, path):
        """Deletes .nf file. UI should confirm first!"""
        Path(path).unlink()

    @classmethod
    def rename_project(cls, old_path, new_name):
        """Renames .nf file. Returns new path."""
        safe_name = cls.sanitize_filename(new_name)
        new_path = cls.PROJECTS_FOLDER / f"{safe_name}.nf"

        if new_path.exists():
            raise FileExistsError(f"Project '{safe_name}' already exists")

        Path(old_path).rename(new_path)
        return new_path

