#!/usr/bin/env python3
# start.py — try multiple module locations and run uvicorn with the first match

import os
import sys
import importlib
from shutil import which

PORT = os.environ.get("PORT", "8000")

# common candidate module paths to try
# Ensure Python can import packages from repo root and backend
root = os.getcwd()
backend_dir = os.path.join(root, "backend")
if os.path.isdir(backend_dir) and backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if os.path.isdir("/app") and "/app" not in sys.path:
    sys.path.insert(0, "/app")

candidates = [
    "app.main",
    "main",
    "src.main",
    "server",
    "backend.main",
    "api.main",
    "app.app",
    "application",
]

found = []
for mod in candidates:
    try:
        m = importlib.import_module(mod)
        for attr in ("app","application","api"):
            if hasattr(m, attr):
                found.append((mod, attr))
                break
        if found:
            break
    except Exception:
        continue

# fallback: scan for files containing "FastAPI("
if not found:
    import pathlib, re
    base_dir = pathlib.Path(os.environ.get("APP_ROOT", os.getcwd()))
    if pathlib.Path("/app").exists():
        base_dir = pathlib.Path("/app")
    pattern = re.compile(r"\bFastAPI\s*\(", re.I)
    for py in list(base_dir.rglob("*.py")):
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            continue
        if pattern.search(text):
            rel = py.relative_to(base_dir)
            mod_name = ".".join(rel.with_suffix("").parts)
            try:
                m = importlib.import_module(mod_name)
                for attr in ("app","application","api"):
                    if hasattr(m, attr):
                        found.append((mod_name, attr))
                        break
                if found:
                    break
            except Exception:
                continue

if not found:
    sys.stderr.write("STARTUP ERROR: Could not locate ASGI app. Tried candidates: {}\n".format(", ".join(candidates)))
    sys.stderr.write("You should have a Python module containing a FastAPI instance named `app` (or `application`).\n")
    try:
        files = os.listdir("/app")
        sys.stderr.write("Files in /app: {}\n".format(files))
    except Exception:
        pass
    sys.exit(2)

mod, attr = found[0]
entry = f"{mod}:{attr}"
sys.stderr.write(f"Found ASGI entrypoint: {entry}\n")
uv = which("uvicorn") or which("uvicorn.exe")
if not uv:
    sys.stderr.write("uvicorn binary not found; using python -m uvicorn\n")
    os.execvp(sys.executable, [sys.executable, "-m", "uvicorn", entry, "--host", "0.0.0.0", "--port", PORT])
else:
    os.execvp(uv, [uv, entry, "--host", "0.0.0.0", "--port", PORT])
