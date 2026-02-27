# ingest_sender.py
# Purpose: Ingest a file asynchronously and push a completion message to a notification queue.

import sys
from pathlib import Path
from client import get_al_client
from config import settings      # to get the notification queue name (settings.nq)


def resolve_input_path(raw_path: str) -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    user_path = Path(raw_path).expanduser()

    candidates = []
    if user_path.is_absolute():
        candidates.append(user_path)

        parts = user_path.parts
        if len(parts) >= 2 and parts[1] == repo_root.name:
            candidates.append(repo_root / Path(*parts[2:]))
    else:
        candidates.append(Path.cwd() / user_path)
        candidates.append(repo_root / user_path)

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(raw_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_sender.py <path_to_file>")
        sys.exit(1)

    raw_path = sys.argv[1]
    try:
        path = resolve_input_path(raw_path)
    except FileNotFoundError:
        repo_root = Path(__file__).resolve().parents[2]
        print(f"File not found: {raw_path}")
        print("Try one of these forms:")
        print(f"  {repo_root / 'data/samples/benign.txt'}")
        print("  data/samples/benign.txt")
        sys.exit(1)

    al = get_al_client()

    # Params for ingest (same schema idea as submit)
    params = {
        "description": "Ingest demo from capstone",
        "services": {"selected": ["Extract", "Safelist"]}  # example services
    }

    # Metadata stored with submission
    metadata = {"source": "capstone", "file_path": str(path)}

    # Ingest call:
    # - This is "fire-and-forget"
    # - nq=settings.nq tells AL to write a message when analysis completes
    ingest_id = al.ingest(path=str(path), nq=settings.nq, params=params, metadata=metadata)

    print("Ingested:", str(path))
    print("Ingest ID:", ingest_id)
    print("Notification queue:", settings.nq)

if __name__ == "__main__":
    main()