"""Per-user physical file storage helpers.

Files are stored under ``data/uploads/<user_id>/<random-internal-name>`` so two
users can upload a file with the same name without collision, and so no path is
ever derived from user-controlled input.
"""
import os
import secrets
from pathlib import Path

from config import UPLOAD_DIR


def user_upload_dir(user_id) -> Path:
    directory = UPLOAD_DIR / str(int(user_id))
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def make_stored_filename(extension: str) -> str:
    """Unique, collision-proof internal filename (keeps the real extension)."""
    extension = extension if extension.startswith(".") else f".{extension}"
    return secrets.token_hex(16) + extension.lower()


def user_file_path(user_id, stored_filename: str) -> Path:
    # basename() neutralises any path traversal even though names are generated.
    safe_name = os.path.basename(stored_filename)
    return user_upload_dir(user_id) / safe_name


def delete_user_file(user_id, stored_filename: str) -> None:
    try:
        path = user_file_path(user_id, stored_filename)
        if path.exists():
            path.unlink()
    except OSError:
        pass


def delete_user_dir(user_id) -> None:
    """Remove the user's whole upload directory (used on account deletion)."""
    import shutil
    try:
        directory = UPLOAD_DIR / str(int(user_id))
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)
    except OSError:
        pass
