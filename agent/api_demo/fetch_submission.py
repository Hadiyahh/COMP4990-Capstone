# fetch_submission.py
# Purpose: Fetch and print the FULL results for a submission id (sid)

import sys
from client import get_al_client

def main():
    # Make sure user provided a submission id
    if len(sys.argv) < 2:
        print("Usage: python fetch_submission.py <sid>")
        sys.exit(1)

    sid = sys.argv[1]  # grab sid from command line
    al = get_al_client()  # authenticated client

    # Fetch full submission record (includes verdict, score, files, results)
    full = al.submission.full(sid)

    # Print useful summary first
    print("SID:", sid)
    print("STATE:", full.get("state"))
    print("COMPLETED:", (full.get("times") or {}).get("completed"))
    print("MAX_SCORE:", full.get("max_score"))
    print("VERDICT:", full.get("verdict"))
    print("FILE_COUNT:", full.get("file_count"))
    print("FILES:", full.get("files"))

    # If you want to see the whole JSON (big), uncomment:
    # import json
    # print(json.dumps(full, indent=2))
    results = full.get("results", [])          # list of per-file results
    
    print("RESULTS_COUNT:", len(results))

    # Show each file + which services produced results
    for i, r in enumerate(results):
        print(f"\n--- Result[{i}] ---")
        print("sha256:", r.get("sha256"))
        print("services:", list((r.get("result") or {}).keys()))
        
if __name__ == "__main__":
    main()

