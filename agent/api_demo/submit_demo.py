# submit_demo.py
# Purpose: Submit a file to Assemblyline using the Submit API.

import sys                      # lets us read command-line arguments (sys.argv)
from client import get_al_client # our helper to connect to Assemblyline

def main():
    # sys.argv is a list like: ["submit_demo.py", "/path/to/file"]
    if len(sys.argv) < 2:
        # If user didn't pass a file path, print correct usage and exit
        print("Usage: python submit_demo.py <path_to_file>")
        sys.exit(1)

    # The file path passed in the terminal
    path = sys.argv[1]

    # Build an authenticated client (uses AL_HOST/AL_USER/AL_APIKEY from .env)
    al = get_al_client()

    # params = submission parameters, same idea as the docs' "settings" dict
    params = {
        # shows up in UI / logs as description of the submission
        "description": "Submit demo from capstone",

        # choose exactly which services run (case-sensitive service names!)
        "services": {"selected": ["Antivirus", "Extraction", "Filtering", "Networking", "Static Analysis"]}
    }

    # metadata = extra key/value fields stored with the submission
    # Putting file_path is a common trick so you can map results back to a file
    metadata = {
        "source": "capstone",
        "file_path": path
    }

    # Submit the file:
    # - path=... is the local path to the file on your machine
    # - params=... controls how AL analyzes it
    # - metadata=... is extra info you want saved with the submission
    res = al.submit(path=path, params=params, metadata=metadata)

    # Print the response so you can inspect:
    # Depending on version, it may include sid or other fields
    print("Submit response:", res)

if __name__ == "__main__":
    # Standard Python pattern: only run main() if executed directly
    main()