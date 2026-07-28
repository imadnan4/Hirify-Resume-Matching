from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = BACKEND_ROOT / "app"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _get_free_port() -> tuple[int, socket.socket]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = int(sock.getsockname()[1])
    return port, sock


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "hirify-test.db"
    upload_root = tmp_path / "uploads"
    port, held_sock = _get_free_port()
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    env["UPLOAD_ROOT"] = str(upload_root)
    env["EMBEDDING_BACKEND"] = "hash"

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=str(BACKEND_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    base_url = f"http://127.0.0.1:{port}"
    startup_error = None
    for _ in range(100):
        if process.poll() is not None:
            startup_error = process.stdout.read() if process.stdout else ""
            break
        try:
            response = httpx.get(f"{base_url}/health", timeout=0.5)
            if response.status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.1)
    else:
        startup_error = "Timed out waiting for Uvicorn startup"

    held_sock.close()

    if startup_error is not None:
        process.terminate()
        process.wait(timeout=5)
        raise RuntimeError(f"Uvicorn failed to start for tests:\n{startup_error}")

    with httpx.Client(base_url=base_url, timeout=30.0) as test_client:
        yield test_client

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
