"""Check the committed tree being pushed, without touching local data or edits."""

import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


def main() -> int:
    root = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
    )
    # Use the project's dependencies, not pre-commit's isolated Python environment.
    candidates = [
        root / ".venv" / "bin" / "python",
        root / ".venv" / "Scripts" / "python.exe",
        root / "venv" / "bin" / "python",
        root / "venv" / "Scripts" / "python.exe",
    ]
    python = next((path for path in candidates if path.is_file()), None)
    if python is None:
        sys.stderr.write(
            "Create .venv and install requirements.txt and requirements-dev.txt "
            "before pushing.\n"
        )
        return 1

    ref = (
        os.environ.get("PRE_COMMIT_TO_REF")
        or os.environ.get("PRE_COMMIT_LOCAL_BRANCH")
        or "HEAD"
    )
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=root, text=True
    ).strip()
    env = {
        **os.environ,
        "TELEGRAM_API_ID": "1",
        "TELEGRAM_API_HASH": "test",
        "TELEGRAM_BOT_TOKEN": "1:test",
        "TELEGRAM_BOT_TOKEN_2": "2:test",
        "ADMINS": "[]",
        "LIMIT_SPAM": "10",
        "ADMIN_TO_UPDATE_OF_PAYMENT": "1",
    }
    with tempfile.TemporaryDirectory(prefix="get-chat-id-push-") as directory:
        snapshot = Path(directory) / "repo"
        snapshot.mkdir()
        archive_path = Path(directory) / "source.tar"
        subprocess.run(
            ["git", "archive", "--output", str(archive_path), commit],
            cwd=root,
            check=True,
        )
        with tarfile.open(archive_path) as archive:
            archive.extractall(snapshot, filter="data")

        # Check, don't fix: edits at push time would not change the existing commit.
        for args in (
            ["ruff", "check", "."],
            ["ruff", "format", "--check", "."],
            ["pytest", "-q"],
        ):
            result = subprocess.run(
                [str(python), "-m", *args],
                cwd=snapshot,
                env=env,
            )
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
