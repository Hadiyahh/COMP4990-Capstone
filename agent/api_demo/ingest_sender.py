# ingest_sender.py
# Purpose: Ingest a file asynchronously and push a completion message to a notification queue.

import sys
from client import get_al_client
from config import settings      # to get the notification queue name (settings.nq)

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_sender.py <path_to_file>")
        sys.exit(1)

    path = sys.argv[1]
    al = get_al_client()

    # Params for ingest (same schema idea as submit)
    params = {
        "description": "Ingest demo from capstone",
        "services": {"selected": ["Extract", "Safelist"]}  # example services
    }

    # Metadata stored with submission
    metadata = {"source": "capstone", "file_path": path}

    # Ingest call:
    # - This is "fire-and-forget"
    # - nq=settings.nq tells AL to write a message when analysis completes
    ingest_id = al.ingest(path=path, nq=settings.nq, params=params, metadata=metadata)

    print("Ingested:", path)
    print("Ingest ID:", ingest_id)
    print("Notification queue:", settings.nq)

if __name__ == "__main__":
    main()