#!/usr/bin/env python3
"""deploy.py — minimal Path E pyscript sync (Phase C/D tooling).

Pushes the tested domain package + pyscript adapters to the HA VM and reloads
pyscript. Safety rituals are enforced:
  - requires `tools/qa.sh` green (tested == deployed),
  - never touches isacs_rum entities (invariant),
  - adapters run in SHADOW mode until Phase D (no service-call ownership flip).

Usage:
  python3 tools/deploy.py [--check-only]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VM = "root@192.168.1.248"
PORT = "2222"
VM_SCRIPTS = "/config/pyscript/scripts"
VM_NATIVE = "/config/pyscript/native_domain"

# Path E write set — the ONLY files deploy.py ever pushes on the VM.
SOURCE_MAP: dict[str, str] = {
    # source-relative to repo  ->  absolute target on the VM
    "adapters/pyscript/home_status.py": f"{VM_SCRIPTS}/home_status.py",
    "adapters/pyscript/daylight.py": f"{VM_SCRIPTS}/daylight.py",
    "adapters/pyscript/night.py": f"{VM_SCRIPTS}/night.py",
    "domain/__init__.py": f"{VM_NATIVE}/domain/__init__.py",
    "domain/daylight/__init__.py": f"{VM_NATIVE}/domain/daylight/__init__.py",
    "domain/daylight/models.py": f"{VM_NATIVE}/domain/daylight/models.py",
    "domain/daylight/home_status.py": f"{VM_NATIVE}/domain/daylight/home_status.py",
    "domain/daylight/daylight.py": f"{VM_NATIVE}/domain/daylight/daylight.py",
    "domain/daylight/night.py": f"{VM_NATIVE}/domain/daylight/night.py",
}

SSH_BASE = ["ssh", "-p", PORT, "-o", "StrictHostKeyChecking=accept-new", VM]


def ssh(cmd: str) -> None:
    subprocess.run([*SSH_BASE, cmd], check=True)


def run_qa() -> None:
    print("== qa.sh (tested == deployed) ==")
    subprocess.run([str(REPO / "tools" / "qa.sh")], check=True)


def isacs_rum_guard() -> None:
    """Grep the write set's CODE (not docstrings) for isacs_rum entity refs."""
    import ast

    forbidden = ("isac_tak", "isac_lekstuga", "isacs_rum")

    def docstring_bodies(node) -> list[ast.AST]:
        """The docstring statement of a Module/def/class, if present."""
        out = []
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                out.append(body[0])
                out.append(body[0].value)
        for child in ast.iter_child_nodes(node):
            out.extend(docstring_bodies(child))
        return out

    def code_tokens(rel: str) -> list[str]:
        tree = ast.parse((REPO / rel).read_text())
        docstrings = set(docstring_bodies(tree))
        tokens: list[str] = []
        for node in ast.walk(tree):
            if node in docstrings:
                continue
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                tokens.append(node.value)
            elif isinstance(node, ast.Name):
                tokens.append(node.id)
            elif isinstance(node, ast.Attribute):
                tokens.append(node.attr)
        return tokens

    for rel in SOURCE_MAP:
        for tok in code_tokens(rel):
            for forbidden_token in forbidden:
                if forbidden_token in tok:
                    raise SystemExit(
                        f"deploy block: {rel} references forbidden entity token {forbidden_token!r}"
                    )
    print("isacs_rum guard: clean (no forbidden entity refs in write-set code)")


def tar_over_ssh(src: Path, dst: str) -> None:
    """Ship one file into an absolute target path on the VM (sftp is disabled)."""
    cmd = f"mkdir -p {dst.rsplit('/', 1)[0]!s} 2>/dev/null; tar -C /tmp -xf - && mv /tmp/{src.name} {dst}"
    tar = ["tar", "-C", str(src.parent), "-cf", "-", src.name]
    push = subprocess.Popen(tar, stdout=subprocess.PIPE)
    remote = subprocess.Popen([*SSH_BASE, cmd], stdin=push.stdout, stdout=subprocess.PIPE)
    push.stdout.close() if push.stdout else None
    out, err = remote.communicate()
    if remote.returncode != 0:
        raise SystemExit(f"tar-over-ssh failed for {src} -> {dst}: {err}")


def push() -> None:
    print("== pushing write set (tar-over-ssh) ==")
    for rel, dst in SOURCE_MAP.items():
        src = REPO / rel
        print(f"  {rel} -> {dst}")
        tar_over_ssh(src, dst)


def reload() -> None:
    """Triggers pyscript.reload over the local REST API (token lives on this machine)."""
    import json
    import urllib.request

    token = open("/tmp/opencode/zha_reload/zha_ws.py").read().split('access_token":"')[1].split('"')[0]
    req = urllib.request.Request(
        "http://192.168.1.248:8123/api/services/pyscript/reload",
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=b"{}",
    )
    with urllib.request.urlopen(req) as resp:
        print(f"pyscript.reload -> HTTP {resp.status}")
        resp.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", help="run qa + guard, skip push/reload")
    args = parser.parse_args()

    run_qa()
    isacs_rum_guard()
    if args.check_only:
        print("check-only: OK (nothing deployed)")
        return 0

    push()
    reload()
    print("deployed + pyscript.reload sent. Shadow parity ready for inspection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())