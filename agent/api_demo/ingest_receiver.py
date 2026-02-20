# ingest_receiver.py
# Purpose: Listen to a notification queue and fetch results when a submission completes.

import time
from client import get_al_client
from config import settings

def main():
    # Make an authenticated client
    al = get_al_client()

    # Display which queue we are listening to
    print("Listening on notification queue:", settings.nq)

    while True:
        # get_message(queue) returns one message or None
        # This is how you avoid polling the whole search API constantly
        msg = al.ingest.get_message(settings.nq)

        # If no message yet, wait a bit and keep looping
        if msg is None:
            time.sleep(1)
            continue

        # Print raw message so you can learn what fields exist in YOUR setup
        print("\n--- Message received ---")
        print(msg)

        # Different setups may store the submission id under different keys
        # These are the most common patterns
        sid = (
            msg.get("sid") or                         # direct "sid"
            msg.get("submission_id") or               # alternative naming
            (msg.get("submission") or {}).get("sid")  # nested object case
        )

        # If we can't find a submission id, you need to inspect msg to see the correct key
        if not sid:
            print("No SID found in message; inspect the message keys above.")
            continue

        # Fetch full results for the submission id
        full = al.submission.full(sid)

        # Print a quick summary
        print("SID:", sid)
        print("Verdict:", full.get("verdict"))
        print("Max score:", full.get("max_score"))

if __name__ == "__main__":
    main()