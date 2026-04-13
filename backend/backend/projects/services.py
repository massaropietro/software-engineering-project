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

    Structure: MEDIA_ROOT/projects/<project_id>/source/
    """
    return Path(settings.MEDIA_ROOT) / "_projects_sources" / str(project.id) / "source"


def _build_file_structure(path: Path, root_path: Path) -> list:
    """
    Recursively scans the directory and returns a JSON-serialisable structure
    (directories first, dotfiles excluded).  No DB writes – files live on disk.
    """
    items = []
    try:
        with os.scandir(path) as it:
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
                    item["children"] = _build_file_structure(entry.path, root_path)
                else:
                    item["size"] = entry.stat().st_size

                items.append(item)
    except OSError as e:
        logger.error(f"Error scanning {path}: {e}")

    return items


def update_project_structure(project) -> None:
    """
    Clones or extracts the project into the persistent media storage directory
    and updates `project.file_structure` with the resulting tree.

    Old source directory is wiped first to keep an exact mirror of the source.
    """
    source_path = get_project_source_path(project)

    # Wipe any previous clone/extraction
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
        logger.warning(f"Project {project.id} has no zip_file or repo_url – empty source dir")

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

_MUTMUT_STATUS_MAP = {
    "Killed": "killed",
    "Survived": "survived",
    "Timeout": "timeout",
    "Suspicious": "suspicious",
    # mutmut may store lowercase too
    "killed": "killed",
    "survived": "survived",
    "timeout": "timeout",
    "suspicious": "suspicious",
}


def _parse_mutmut_v3_results(mutants_path: Path) -> list[dict]:
    """
    Parses Mutmut 3.0+ results, which are stored in distributed .py.meta JSON files
    inside the mutants/ directory.
    """
    results = []
    if not mutants_path.exists():
        logger.warning(f"Mutants directory not found at {mutants_path}")
        return results

    meta_files = list(mutants_path.rglob("*.py.meta"))
    logger.info(f"Scanning {len(meta_files)} .meta files for Mutmut 3.0 results in {mutants_path}")

    for meta_file in meta_files:
        try:
            with open(meta_file, "r") as f:
                data = json.load(f)
            
            # The mutated file is the .meta file without the .meta suffix
            mutated_file_path = meta_file.with_suffix("")
            try:
                rel_path = mutated_file_path.relative_to(mutants_path)
            except ValueError:
                rel_path = mutated_file_path
            
            # Attempt to read the mutated file to recover approximate line numbers
            mutated_lines = []
            if mutated_file_path.exists():
                try:
                    with open(mutated_file_path, "r", encoding="utf-8") as mf:
                        mutated_lines = mf.readlines()
                except Exception:
                    pass

            exit_codes = data.get("exit_code_by_key", {})
            for key, exit_code in exit_codes.items():
                # Mutmut 3.0 status mapping (confirmed by frequency analysis):
                # 33: Survived (🫥)
                # 1: Killed (🎉)
                # -24: Timeout (SIGXCPU) - counted as Killed (🎉) in mutmut summary
                # others: Error
                
                if exit_code == 33:
                    status = "survived"
                elif exit_code == 1:
                    status = "killed"
                elif exit_code == -24:
                    status = "timeout"
                else:
                    status = "suspicious"
                
                # Try to find the mutant's line in the mutated file
                line_no = 0
                if mutated_lines:
                    # Mutmut 3.0+ uses a signature like 'def xǁClassNameǁmethod__mutmut_1'
                    # The key often looks like 'module.ClassName.method__mutmut_1'
                    # We'll search for the last part of the key.
                    search_term = key.split(".")[-1]
                    for i, l in enumerate(mutated_lines):
                        if search_term in l and "def " in l:
                            line_no = i + 1
                            break

                results.append({
                    "mutant_id": key,
                    "file": str(rel_path),
                    "line": line_no,
                    "status": status,
                    "exit_code": exit_code,
                    "description": f"Exit code: {exit_code}"
                })
        except Exception as e:
            logger.error(f"Failed to parse mutmut v3 meta file {meta_file}: {e}")
    
    return results


def get_mutant_diff(mutant) -> str:
    """
    Extracts the original and mutated function source from a Mutmut 3.0+ "trampoline" file
    and returns a unified diff.
    """
    source_path = get_project_source_path(mutant.analysis.project)
    mutants_path = source_path / "mutants"
    mutated_file_path = mutants_path / mutant.file
    
    if not mutated_file_path.exists():
        logger.warning(f"Mutated file not found at {mutated_file_path}")
        return f"Mutated file not found: {mutant.file}"

    try:
        with open(mutated_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Failed to read {mutated_file_path}: {e}")
        return f"Failed to read file: {e}"

    # mutant_id is like 'flask_caching.Cache.__init____mutmut_1'
    # The 'trampoline' setup uses markers like 'def xǁCacheǁ__init____mutmut_orig'
    # and 'def xǁCacheǁ__init____mutmut_1'.
    
    # Extract the last part of the dot-separated ID for signature matching
    # key often ends in __mutmut_N. The function name is before it.
    mutant_id_parts = mutant.mutant_id.split("__mutmut_")
    if len(mutant_id_parts) < 2:
        return f"Unexpected mutant ID format: {mutant.mutant_id}"
    
    mutant_index = mutant_id_parts[1]
    func_sig_part = mutant_id_parts[0].split(".")[-1]
    
    # Correct signature components for Mutmut 3.0+ 
    # Use just the relevant part for matching
    orig_sig = f"{func_sig_part}__mutmut_orig"
    mutant_sig = f"{func_sig_part}__mutmut_{mutant_index}"
    
    def extract_func_block(signature):
        start_idx = -1
        for idx, line in enumerate(lines):
            if f"def {signature}" in line:
                start_idx = idx
                break
        
        if start_idx == -1:
            return None
        
        # Capture lines while indentation is greater than the 'def' line
        # and doesn't hit another 'def' at the same level
        func_block = []
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        func_block.append(lines[start_idx])
        
        for k in range(start_idx + 1, len(lines)):
            line = lines[k]
            if not line.strip():
                func_block.append(line)
                continue
                
            current_indent = len(line) - len(line.lstrip())
            # Stop if we hit a 'def ' at same/lower level or something with lower indent
            if current_indent <= base_indent and "def " in line:
                break
            if current_indent < base_indent:
                break
            
            func_block.append(line)
        return func_block

    orig_block = extract_func_block(orig_sig)
    mut_block = extract_func_block(mutant_sig)
    
    if not orig_block or not mut_block:
        return f"Could not extract function source for {mutant.mutant_id} within {mutant.file}"

    # Generate unified diff
    diff = difflib.unified_diff(
        orig_block,
        mut_block,
        fromfile=f"{mutant.file} (original)",
        tofile=f"{mutant.file} (mutant {mutant_index})",
    )
    return "".join(diff)


def _parse_mutmut_results(cache_path: Path) -> list[dict]:
    """
    Reads the `.mutmut-cache` SQLite database produced by mutmut and returns
    a list of mutant dicts.
    """
    results = []
    if not cache_path.exists():
        logger.warning(f"mutmut cache not found at {cache_path}")
        return results

    try:
        conn = sqlite3.connect(str(cache_path))
        cursor = conn.cursor()

        # mutmut stores results in a table depending on version.
        # Try the standard schema first.
        try:
            cursor.execute(
                "SELECT id, source_path, line_number, status FROM mutant"
            )
            rows = cursor.fetchall()
            for mutant_id, source, line, status in rows:
                results.append(
                    {
                        "mutant_id": str(mutant_id),
                        "file": source or "",
                        "line": line,
                        "status": _MUTMUT_STATUS_MAP.get(status, "survived"),
                        "description": "",
                    }
                )
        except sqlite3.OperationalError:
            # Fallback: try alternate schema seen in some mutmut versions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            logger.warning(f"Unexpected mutmut cache schema. Tables found: {tables}")

        conn.close()
    except Exception as e:
        logger.error(f"Failed to parse mutmut cache at {cache_path}: {e}")

    return results


def _install_project_dependencies(project_path: Path) -> None:
    """
    Installs Python dependencies for the project if a requirements.txt,
    setup.py, or pyproject.toml is present, into a temporary location.
    Uses uv pip install (primary) or pip install --target.
    """
    deps_target = project_path / ".mutmut_deps"
    deps_target.mkdir(exist_ok=True)

    # We prefer 'uv' as it's faster and present in our Docker image.
    # We fallback to 'pip' if for some reason 'uv' is not available.
    def run_install(args: list[str]) -> bool:
        # Try uv first
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

        # Fallback to pip
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

    # 1. Try common requirements files
    req_files = ["requirements.txt", "requirements-dev.txt", "test-requirements.txt", "requirements-test.txt"]
    for rf in req_files:
        if (project_path / rf).exists():
            logger.info(f"Installing dependencies from {rf} for {project_path}")
            run_install(["-r", rf])

    # 2. Try setup.py or pyproject.toml with common extras
    if (project_path / "setup.py").exists() or (project_path / "pyproject.toml").exists():
        logger.info(f"Installing project itself with potential extras for {project_path}")
        # Try base installation first
        run_install(["."])
        # Try common test extras which might contain 'pytest', 'simplejson', etc.
        for extra in ["test", "tests", "dev"]:
            run_install([f".[ {extra}]"])


def run_mutation_analysis(analysis) -> None:
    """
    Runs mutmut on the project source and stores results in MutationResult rows.

    Steps:
    1. Locate the persistent source directory.
    2. Optionally install project deps.
    3. Build the mutmut command (paths-to-mutate from analysis.files).
    4. Execute mutmut run.
    5. Parse .mutmut-cache SQLite → create MutationResult rows.
    6. Compute mutation score, store raw_output.
    """
    from backend.projects.models import MutationResult  # avoid circular at module level

    source_path = get_project_source_path(analysis.project)

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source directory for project {analysis.project.id} not found at {source_path}. "
            "Run build_filesystem_task first."
        )

    # Install dependencies so the project's tests can be discovered
    _install_project_dependencies(source_path)

    # Remove OS resource limits (CPU time, Memory, File size) to ensure complete runs
    for limit_name in ["RLIMIT_CPU", "RLIMIT_AS", "RLIMIT_DATA", "RLIMIT_FSIZE"]:
        try:
            if hasattr(resource, limit_name):
                limit_attr = getattr(resource, limit_name)
                # Try to set soft and hard limits to infinity
                try:
                    resource.setrlimit(limit_attr, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
                    logger.info(f"Successfully set {limit_name} to infinity")
                except Exception:
                    # If increasing hard limit is not allowed (non-root), set soft to current hard max
                    _, hard = resource.getrlimit(limit_attr)
                    resource.setrlimit(limit_attr, (hard, hard))
                    logger.info(f"Successfully set {limit_name} to maximum allowed: {hard}")
        except Exception as e:
            logger.warning(f"Failed to adjust {limit_name}: {e}")

    # Build PYTHONPATH so mutmut/pytest can import project modules
    deps_target = source_path / ".mutmut_deps"
    env = os.environ.copy()
    
    # ISOLATION: Remove Django-related environment variables to prevent 
    # pytest-django (if installed in the worker) from interfering.
    django_vars = [
        "DJANGO_SETTINGS_MODULE",
        "DATABASE_URL",
        "DJANGO_SECRET_KEY",
        "DJANGO_DEBUG",
        "DJANGO_ALLOWED_HOSTS",
    ]
    for var in django_vars:
        env.pop(var, None)

    # Prepare setup.cfg for mutmut 3.0+ compatibility
    # Mutmut 3.0+ removed most CLI flags in favor of configuration files
    setup_cfg_path = source_path / "setup.cfg"
    config = configparser.ConfigParser()
    if setup_cfg_path.exists():
        config.read(setup_cfg_path)

    if "mutmut" not in config:
        config["mutmut"] = {}

    if analysis.files:
        paths_to_mutate = ",".join(analysis.files)
    elif (source_path / "src").is_dir():
        paths_to_mutate = "src"
    else:
        # Fallback: list all top-level items EXCEPT known non-source/build/test items
        items = []
        exclude = {
            "mutants", ".mutmut_deps", "tests", "test", "venv", ".venv", ".git", 
            "setup.py", "conftest.py", "tox.ini", "setup.cfg", "pyproject.toml",
            "__pycache__", ".pytest_cache", ".mypy_cache"
        }
        for item in source_path.iterdir():
            if item.name in exclude or item.name.startswith("."):
                continue
            if item.is_dir() or (item.is_file() and item.suffix == ".py"):
                items.append(item.name)
        paths_to_mutate = ",".join(items) if items else "."

    config["mutmut"]["paths_to_mutate"] = paths_to_mutate
    config["mutmut"]["pytest_add_cli_args_test_selection"] = "."
    config["mutmut"]["runner"] = "python -m pytest"
    config["mutmut"]["dict_synonyms"] = "dict"
    # ENABLING DEBUG: will show us the full pytest command line in mutmut stderr
    config["mutmut"]["debug"] = "True"

    with open(setup_cfg_path, "w") as f:
        config.write(f)

    # CRITICAL: Mutmut 3.0+ runs from 'mutants' subfolder but doesn't copy configs!
    # Without these, pytest fails to identify the project layout or discovery rules.
    mutants_path = source_path / "mutants"
    mutants_path.mkdir(exist_ok=True)
    for cfg_file in ["pyproject.toml", "setup.cfg", "pytest.ini", "tox.ini"]:
        src_cfg = source_path / cfg_file
        if src_cfg.exists():
            shutil.copy2(src_cfg, mutants_path / cfg_file)

    # Build PYTHONPATH for dependencies and mutated source
    # We include 'mutants/src' for src-layout projects and 'mutants' for flat ones.
    # CRITICAL: mutated source MUST come before installed dependencies.
    python_paths = [str(mutants_path / "src"), str(mutants_path)]
    if deps_target.exists():
        python_paths.append(str(deps_target))
        
    env["PYTHONPATH"] = os.pathsep.join(python_paths + [env.get("PYTHONPATH", "")])
    
    # GLOBAL ISOLATION: Use PYTEST_ADDOPTS to force flags and discovery
    # This is more reliable than overwriting pytest.ini, as it preserves
    # the original project configuration (like testpaths in pyproject.toml).
    pytest_addopts = [
        "-p no:django",
        "-p no:sugar",
        "-p no:cov",
        "-p no:anyio",
        "-p no:faker",
        "--ignore=mutants",
        "--ignore=.mutmut_deps",
        "--ignore=tests/mypy_test_cases",
        "--ignore=tests/typing",
        "--ignore=tests/test_init.py",
        "--ignore=tests/test_app.py",
    ]
    env["PYTEST_ADDOPTS"] = " ".join(pytest_addopts + [env.get("PYTEST_ADDOPTS", "")])

    cmd = ["mutmut", "run"]

    logger.info(f"Running mutmut for analysis {analysis.id}: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        cwd=str(source_path),
        env=env,
        capture_output=True,
        text=True,
    )

    raw_output = result.stdout + result.stderr
    analysis.raw_output = raw_output
    analysis.save(update_fields=["raw_output"])

    logger.info(f"mutmut stdout:\n{result.stdout}")
    if result.stderr:
        logger.warning(f"mutmut stderr:\n{result.stderr}")

    # Parse results: try legacy SQLite cache first, then Mutmut 3.0+ meta files
    cache_path = source_path / ".mutmut-cache"
    mutants = _parse_mutmut_results(cache_path)
    
    if not mutants:
        mutants = _parse_mutmut_v3_results(source_path / "mutants")

    if not mutants:
        logger.warning(f"No mutants found for analysis {analysis.id}")

    # Bulk-create MutationResult rows
    result_objs = [
        MutationResult(
            analysis=analysis,
            mutant_id=m["mutant_id"],
            file=m["file"],
            line=m["line"],
            status=m["status"],
            description=m.get("description", ""),
        )
        for m in mutants
    ]
    MutationResult.objects.bulk_create(result_objs, ignore_conflicts=True)

    # Compute mutation score: (killed + timeout) / (killed + survived + timeout + suspicious)
    total = len(mutants)
    killed_count = sum(1 for m in mutants if m["status"] in ["killed", "timeout"])
    analysis.score = round(killed_count / total * 100, 2) if total > 0 else None
    analysis.save(update_fields=["score"])

    logger.info(
        f"Analysis {analysis.id} complete: {killed_count}/{total} mutants killed or timed out "
        f"(score={analysis.score})"
    )
