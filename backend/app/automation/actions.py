from pathlib import Path
from urllib.parse import quote_plus, urlparse
import os
import shutil
import subprocess
import webbrowser

ALLOWED_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
}

def _windows_only():
    if os.name != "nt":
        raise RuntimeError("Windows automation is available only on Windows.")

def _safe_path(value: str) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        raise ValueError("File paths must be absolute Windows paths.")
    return p.resolve()

def open_app(app: str):
    _windows_only()
    key = app.strip().lower()
    if key not in ALLOWED_APPS:
        raise ValueError("App is not on the AETHER allowlist.")
    subprocess.Popen([ALLOWED_APPS[key]], close_fds=True)
    return {"action": "open_app", "app": key}

def open_url(url: str):
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Only http and https URLs are allowed.")
    webbrowser.open(url.strip())
    return {"action": "open_url", "url": url.strip()}

def search_web(query: str):
    q = query.strip()
    if not q:
        raise ValueError("Search query is empty.")
    url = "https://www.google.com/search?q=" + quote_plus(q)
    return open_url(url)

def open_folder(path: str):
    _windows_only()
    p = _safe_path(path)
    if not p.exists() or not p.is_dir():
        raise ValueError("Folder does not exist.")
    os.startfile(str(p))
    return {"action": "open_folder", "path": str(p)}

def search_files(path: str, pattern: str = "*", limit: int = 100):
    root = _safe_path(path)
    if not root.exists() or not root.is_dir():
        raise ValueError("Search folder does not exist.")
    limit = max(1, min(limit, 500))
    matches = []
    for item in root.rglob(pattern or "*"):
        matches.append(str(item))
        if len(matches) >= limit:
            break
    return {"action": "search_files", "path": str(root), "pattern": pattern, "results": matches}

def create_folder(path: str):
    p = _safe_path(path)
    if p.exists():
        raise ValueError("Target already exists.")
    p.mkdir(parents=False)
    return {"action": "create_folder", "path": str(p)}

def create_file(path: str):
    p = _safe_path(path)
    if p.exists():
        raise ValueError("Target already exists.")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch()
    return {"action": "create_file", "path": str(p)}

def rename_file(path: str, new_name: str):
    p = _safe_path(path)
    if not p.exists():
        raise ValueError("Source does not exist.")
    name = Path(new_name).name
    if name != new_name or not name.strip():
        raise ValueError("New name must be a simple file or folder name.")
    target = p.with_name(name)
    if target.exists():
        raise ValueError("Target already exists.")
    p.rename(target)
    return {"action": "rename_file", "path": str(p), "new_path": str(target)}

def copy_file(source: str, destination: str):
    src = _safe_path(source)
    dst = _safe_path(destination)
    if not src.exists() or not src.is_file():
        raise ValueError("Source file does not exist.")
    if dst.exists():
        raise ValueError("Destination already exists.")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {"action": "copy_file", "source": str(src), "destination": str(dst)}

def move_file(source: str, destination: str):
    src = _safe_path(source)
    dst = _safe_path(destination)
    if not src.exists():
        raise ValueError("Source does not exist.")
    if dst.exists():
        raise ValueError("Destination already exists.")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return {"action": "move_file", "source": str(src), "destination": str(dst)}

def delete_file(path: str):
    p = _safe_path(path)
    if not p.exists() or not p.is_file():
        raise ValueError("Only an existing file can be deleted.")
    p.unlink()
    return {"action": "delete_file", "path": str(p)}
