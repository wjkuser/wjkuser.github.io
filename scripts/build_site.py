from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOME_DIR = ROOT / "home"
PUBLIC_DIR = ROOT / "public"
BLOG_DIR = PUBLIC_DIR / "one-thousand-and-one-nights"


def ensure_inside(child: Path, parent: Path) -> None:
    resolved_child = child.resolve()
    resolved_parent = parent.resolve()
    if resolved_child != resolved_parent and resolved_parent not in resolved_child.parents:
        raise RuntimeError(f"Refusing to operate outside workspace: {resolved_child}")


def run_mkdocs_build(dirty: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", "mkdocs", "build", "--site-dir", str(BLOG_DIR)]
    if dirty:
        command.insert(4, "--dirty")

    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def print_process_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)


def main() -> None:
    ensure_inside(PUBLIC_DIR, ROOT)

    PUBLIC_DIR.mkdir(exist_ok=True)
    shutil.copytree(HOME_DIR, PUBLIC_DIR, dirs_exist_ok=True)

    try:
        result = run_mkdocs_build()
    except subprocess.CalledProcessError as error:
        combined_output = f"{error.stdout or ''}\n{error.stderr or ''}"
        if "PermissionError" not in combined_output and "WinError 5" not in combined_output:
            print_process_output(error)
            raise

        print("Clean build hit a Windows file lock; retrying MkDocs with --dirty for local preview.")
        result = run_mkdocs_build(dirty=True)

    print_process_output(result)

    print(f"Built combined site at {PUBLIC_DIR}")
    print(f"Homepage: {PUBLIC_DIR / 'index.html'}")
    print(f"Blog: {BLOG_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
