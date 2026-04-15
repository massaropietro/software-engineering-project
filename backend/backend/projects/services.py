import sqlite3
import subprocess
import shutil
import zipfile
import os
import logging
import configparser
import sys
import json
import resource
import difflib
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Project filesystem helpers
# ---------------------------------------------------------------------------

def get_project_source_path(project) -> Path:
    """
    Returns the persistent path where the project source code lives.
    This is a subdirectory inside Django's MEDIA_ROOT so files survive
    across requests and are accessible by Celery workers.
    """
    return Path(settings.MEDIA_ROOT) / "_projects_sources" / str(project.id) / "source"


def _build_file_structure(path: Path, root_path: Path) -> list:
    """
    Recursively scans the directory and returns a JSON-serialisable structure.
    Each directory entry includes a 'total_files' field representing the
    recursive count of all files within it.
    """
    items = []
    try:
        with os.scandir(path) as it:
            # Ordina: prima le directory, poi i file, entrambi in ordine alfabetico
            entries = sorted(it, key=lambda e: (not e.is_dir(), e.name.lower()))

            for entry in entries:
                if entry.name.startswith("."):
                    continue

                rel_path = os.path.relpath(entry.path, root_path)
                item = {
                    "name": entry.name,
                    "path": rel_path,
                    "type": "directory" if entry.is_dir() else "file",
                }

                if entry.is_dir():
                    # Chiamata ricorsiva per ottenere i figli
                    children = _build_file_structure(entry.path, root_path)
                    item["children"] = children

                    # Calcola il totale: somma dei total_files dei figli (se directory)
                    # + 1 per ogni figlio che è un file
                    count = 0
                    for child in children:
                        if child["type"] == "directory":
                            count += child.get("total_files", 0)
                        else:
                            count += 1
                    item["total_files"] = count
                else:
                    item["size"] = entry.stat().st_size

                items.append(item)
    except OSError as e:
        logger.error(f"Error scanning {path}: {e}")

    return items

def update_project_structure(project) -> None:
    """
    Clones or extracts the project into the persistent media storage directory.
    """
    source_path = get_project_source_path(project)

    if source_path.exists():
        shutil.rmtree(source_path)
    source_path.mkdir(parents=True, exist_ok=True)

    if project.zip_file:
        logger.info(f"Extracting zip for project {project.id} → {source_path}")
        try:
            zip_path = project.zip_file.path
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(source_path)
        except (NotImplementedError, ValueError):
            with project.zip_file.open("rb") as f:
                with zipfile.ZipFile(f, "r") as zf:
                    zf.extractall(source_path)

    elif project.repo_url:
        logger.info(f"Cloning {project.repo_url} for project {project.id} → {source_path}")
        try:
            subprocess.check_call(
                ["git", "clone", "--depth", "1", project.repo_url, str(source_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed for project {project.id}: {e}")
            raise
    else:
        logger.warning(f"Project {project.id} has no zip_file or repo_url")

    structure = _build_file_structure(source_path, source_path)
    project.file_structure = structure
    project.save(update_fields=["file_structure"])
    logger.info(f"Project {project.id} source ready at {source_path}")


def get_file_content_from_source(project, file_path: str) -> str:
    """Read a specific file from the project source directory."""
    source_path = get_project_source_path(project)
    full_path = source_path / file_path

    try:
        if not full_path.resolve().is_relative_to(source_path.resolve()):
            raise ValueError("Invalid file path.")
    except Exception:
        raise ValueError("Invalid file path.")

    if not full_path.exists() or not full_path.is_file():
        raise FileNotFoundError("File not found.")

    try:
        return full_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "<Binary file or unsupported encoding>"


# ---------------------------------------------------------------------------
# Mutation analysis
# ---------------------------------------------------------------------------

def _normalize_mutmut_status(raw_status: str) -> str:
    """
    Estrae lo status reale pulendolo da prefissi come 'ok_' o 'bad_'
    utilizzati dallo schema Pony ORM.
    """
    if not raw_status:
        return "survived"

    rs = str(raw_status).lower()

    if "killed" in rs:
        return "killed"
    if "timeout" in rs:
        return "timeout"
    if "suspicious" in rs:
        return "suspicious"

    return "survived"


import sqlite3


def get_mutant_diff(mutant) -> str:
    """
    Estrae le informazioni sulla mutazione leggendo direttamente il DB SQLite.
    Bypassa la CLI di mutmut per evitare errori di versione.
    """
    source_path = get_project_source_path(mutant.analysis.project)
    cache_path = next(source_path.rglob(".mutmut-cache"), None)

    if not cache_path:
        return "Errore: file .mutmut-cache non trovato."

    try:
        conn = sqlite3.connect(str(cache_path))
        cursor = conn.cursor()

        # Prendiamo la riga originale salvata da mutmut 2.x
        query = """
            SELECT Line.line, Line.line_number, SourceFile.filename
            FROM Mutant
            JOIN Line ON Mutant.line = Line.id
            JOIN SourceFile ON Line.sourcefile = SourceFile.id
            WHERE Mutant.id = ?
        """
        cursor.execute(query, (mutant.mutant_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            line_content, line_no, filename = row
            return f"File: {filename}\nLine: {line_no}\nOriginal Code: {line_content.strip()}"

        return "Dati mutante non trovati nel database."
    except Exception as e:
        return f"Errore lettura DB: {str(e)}"

def _parse_mutmut_results(cache_path: Path) -> list[dict]:
    """
    Reads the `.mutmut-cache` SQLite database produced by mutmut 2.x.
    Uses the exact Pony ORM schema provided.
    """
    results = []
    if not cache_path.exists():
        logger.warning(f"mutmut cache not found at {cache_path}")
        return results

    try:
        conn = sqlite3.connect(str(cache_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Query ottimizzata per Mutmut 2.x Schema
            query = """
                SELECT
                    Mutant.id AS mutant_id,
                    SourceFile.filename AS file,
                    Line.line_number AS line,
                    Mutant.status AS status
                FROM Mutant
                JOIN Line ON Mutant.line = Line.id
                JOIN SourceFile ON Line.sourcefile = SourceFile.id
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                results.append(
                    {
                        "mutant_id": str(row["mutant_id"]),
                        "file": row["file"] or "",
                        "line": row["line"] or 0,
                        # Usiamo la nuova funzione per processare "ok_killed" e soci
                        "status": _normalize_mutmut_status(row["status"]),
                        "description": "",
                    }
                )
        except sqlite3.OperationalError as e:
            logger.warning(f"Unexpected mutmut cache schema error: {e}")

        conn.close()
    except Exception as e:
        logger.error(f"Failed to parse mutmut cache at {cache_path}: {e}")

    return results


def _install_project_dependencies(project_path: Path) -> None:
    """
    Installs Python dependencies for the project using uv or pip.
    """
    deps_target = project_path / ".mutmut_deps"
    deps_target.mkdir(exist_ok=True)

    def run_install(args: list[str]) -> bool:
        try:
            res = subprocess.run(
                ["uv", "pip", "install", "--target", str(deps_target), "--quiet"] + args,
                cwd=str(project_path),
                check=False,
                capture_output=True,
            )
            if res.returncode == 0:
                return True
        except FileNotFoundError:
            pass

        try:
            res = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--target", str(deps_target), "--quiet", "--no-input"] + args,
                cwd=str(project_path),
                check=False,
                capture_output=True,
            )
            return res.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

    req_files = ["requirements.txt", "requirements-dev.txt", "test-requirements.txt", "requirements-test.txt"]
    for rf in req_files:
        if (project_path / rf).exists():
            run_install(["-r", rf])

    if (project_path / "setup.py").exists() or (project_path / "pyproject.toml").exists():
        run_install(["."])
        for extra in ["test", "tests", "dev"]:
            run_install([f".[ {extra}]"])


def run_mutation_analysis(analysis) -> None:
    from backend.projects.models import MutationResult

    source_path = get_project_source_path(analysis.project)

    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found at {source_path}.")

    cache_path = next(source_path.rglob(".mutmut-cache"), None)

    if not cache_path or not cache_path.exists():
        logger.warning(f"No mutants found in cache for analysis {analysis.id}")
        MutationResult.objects.filter(analysis=analysis).delete()
        return

    all_mutants = _parse_mutmut_results(cache_path)

    if not all_mutants:
        logger.warning(f"No mutants found in cache for analysis {analysis.id}")
        MutationResult.objects.filter(analysis=analysis).delete()
        return

    filtered_mutants = []

    if analysis.files and not (len(analysis.files) == 1 and analysis.files[0] == '/'):
        for m in all_mutants:
            filepath = m["file"]
            keep = False

            for fpath in analysis.files:
                clean_path = fpath[1:] if fpath.startswith('/') else fpath

                if clean_path.endswith('.py'):
                    if filepath == clean_path:
                        keep = True
                        break
                else:
                    dir_path = clean_path if clean_path.endswith('/') else clean_path + '/'
                    if filepath.startswith(dir_path):
                        keep = True
                        break

            if keep:
                filtered_mutants.append(m)
    else:
        filtered_mutants = all_mutants

    if not filtered_mutants:
        logger.warning(f"Nessun mutante corrisponde ai filtri {analysis.files} per l'analisi {analysis.id}")
        MutationResult.objects.filter(analysis=analysis).delete()
        return

    total = len(filtered_mutants)
    killed_count = sum(1 for m in filtered_mutants if m["status"] in ["killed", "timeout"])
    analysis.score = round(killed_count / total * 100, 2) if total > 0 else 0.0
    analysis.save(update_fields=["score"])

    survived_mutants = [m for m in filtered_mutants if m["status"] == "survived"]
    mutants_to_save = survived_mutants[:20]

    MutationResult.objects.filter(analysis=analysis).delete()

    if mutants_to_save:
        result_objs = [
            MutationResult(
                analysis=analysis,
                mutant_id=m["mutant_id"],
                file=m["file"],
                line=m["line"],
                status=m["status"],
                description=m.get("description", ""),
            )
            for m in mutants_to_save
        ]
        MutationResult.objects.bulk_create(result_objs)

    from backend.projects.analyzer import process_equivalent_mutants
    process_equivalent_mutants(analysis, source_path)

    logger.info(
        f"Analysis {analysis.id} complete: Saved exactly {len(mutants_to_save)} survived mutants for processing "
        f"(Real Overall Score={analysis.score}%)"
    )
