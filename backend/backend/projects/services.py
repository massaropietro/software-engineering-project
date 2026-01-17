import tempfile
import zipfile
import subprocess
import shutil
import os
import logging
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

@contextmanager
def project_filesystem(project):
    """
    Context manager that yields the path to the project's files.
    - If zip_file is present: extracts it to a temporary directory.
    - If repo_url is present: clones the repo to a temporary directory.

    The temporary directory is cleaned up upon exit.

    Usage:
        with project_filesystem(project) as root_path:
            # do something with root_path
            for file in root_path.rglob('*.py'):
                print(file)
    """
    # Create a temporary directory
    tmp_dir = tempfile.mkdtemp(prefix=f"project_{project.id}_")
    try:
        if project.zip_file:
            logger.info(f"Extracting zip file for project {project.id} to {tmp_dir}")
            # Ensure the file is actually on disk (for local dev) or read from stream
            try:
                # Assuming local storage or accessible path
                zip_path = project.zip_file.path
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
            except (NotImplementedError, ValueError):
                # Fallback for storage backends without direct path access (e.g. S3)
                # We open the file stream and extract
                with project.zip_file.open('rb') as f:
                    with zipfile.ZipFile(f, 'r') as zip_ref:
                        zip_ref.extractall(tmp_dir)

            yield Path(tmp_dir)

        elif project.repo_url:
            logger.info(f"Cloning repo {project.repo_url} for project {project.id} to {tmp_dir}")
            try:
                subprocess.check_call(
                    ['git', 'clone', '--depth', '1', project.repo_url, tmp_dir],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"Git clone failed: {e}")
                raise

            yield Path(tmp_dir)

        else:
            logger.warning(f"Project {project.id} has no zip_file or repo_url")
            yield Path(tmp_dir) # Empty dir

    except Exception as e:
        logger.error(f"Error preparing filesystem for project {project.id}: {e}")
        raise
    finally:
        logger.info(f"Cleaning up temp dir {tmp_dir} for project {project.id}")
        shutil.rmtree(tmp_dir, ignore_errors=True)

def build_file_structure(path):
    """
    Recursively scans the directory and returns a JSON-serializable structure.
    """
    items = []
    # Sort directories first, then files
    try:
        # scandir is efficient
        with os.scandir(path) as it:
            entries = sorted(it, key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith('.'): # Skip dotfiles/dirs for now
                    continue

                item = {
                    "name": entry.name,
                    "path": entry.path, # This is absolute, we will clean it later
                    "type": "directory" if entry.is_dir() else "file",
                }

                if entry.is_dir():
                    item["children"] = build_file_structure(entry.path)

                items.append(item)
    except OSError as e:
        logger.error(f"Error scanning {path}: {e}")

    return items


def update_project_structure(project):
    """
    Updates the project's file_structure field by extracting/cloning the source.
    """
    with project_filesystem(project) as root_path:
        # We need to relativize paths to the root_path to avoid leaking system paths
        # and to make them useful for the frontend

        full_structure = build_file_structure(root_path)

        def clean_paths(items, root):
            for item in items:
                # Make path relative to root
                # item['path'] is currently absolute from scandir
                rel_path = os.path.relpath(item['path'], root)
                item['path'] = rel_path
                if 'children' in item:
                    clean_paths(item['children'], root)

        clean_paths(full_structure, root_path)

        project.file_structure = full_structure
        project.save(update_fields=["file_structure"])
