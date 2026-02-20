## Setup
```bash
cd agent/al_api_demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your real AL_HOST/AL_USER/AL_APIKEY
Submit API demo
python submit_demo.py /path/to/file.pptx
Fetch results by SID
python fetch_submission.py <sid>
Ingest API demo (async)

Terminal 1:

python ingest_receiver.py

Terminal 2:

python ingest_sender.py /path/to/file.pptx

---

# How this maps to what the docs taught you
- `client.py` = “Connecting to Assemblyline”
- `submit_demo.py` = “Submit”
- `ingest_sender.py` + `ingest_receiver.py` = “Ingest with notification queue”
- `fetch_submission.py` = “Submission details”

So yes: you’re literally implementing the docs, but in a clean project.

---

## One important reality check
The **exact shape** of:
- the `submit()` response
- the notification message from `nq`
can vary.

That’s why `ingest_receiver.py` prints the raw message first.

____________________________________________________________________________________________________
EXPLANATION 

built and tested an agent/api_demo module that proves we can talk to our local Assemblyline instance through the API.

What works end-to-end now:

Load Assemblyline connection settings from .env (host/user/apikey/ssl verify).

Submit a file to Assemblyline via the Python client (Submit API).

Get back a sid (submission id).

Fetch submission status/results by sid until it shows completed.

This gives us the exact data we need for Phase 2: state, max_score, verdict, file hashes, etc.

Key outputs from the test:

Submitting benign.txt returned sid=2feU1ej1nLIMqbU320XmUR

Fetching by sid showed STATE: completed, MAX_SCORE: 0 (as expected for benign)

This unblocks:

Building the FastAPI /submit endpoint (Phase 1 baseline) by calling these scripts/functions

Building RiskProfile extraction (Phase 2) from the fetched submission JSON

Folder: agent/api_demo/ contains submit + fetch scripts, plus optional ingest sender/receiver scripts for async workflows.

What each file in agent/api_demo does
.env.example

Template of the environment variables you must set (host/user/apikey, etc).
You copy this to .env and fill in your values.

.env

Your real local credentials + settings. Should not be committed.
Typical fields:

AL_HOST (example: https://localhost)

AL_USER (example: admin)

AL_APIKEY (your API key)

AL_VERIFY_SSL (false if you’re on self-signed localhost)

AL_NOTIFICATION_QUEUE (only needed for ingest async demo)

requirements.txt

Python dependencies for just this demo folder (ex: assemblyline_client, python-dotenv, etc).
Installed inside the venv.

.gitignore

Keeps secrets and junk out of git (usually includes .env, __pycache__/, etc).

config.py

Reads environment variables (via dotenv) and exposes settings to the rest of the code.
This is where AL_HOST, AL_USER, AL_APIKEY, SSL verify flag, notification queue name, etc get centralized.

client.py

Creates and returns a configured Assemblyline client object:

calls get_client(...)

passes server, (user, apikey), and SSL verify behavior
Everything else imports this so we don’t duplicate connection logic.

submit_demo.py

Synchronous submission demo using the Submit API:

takes a file path argument

calls al.submit(path=..., params=..., metadata=...)

prints the response (includes sid)
Use this when you want the system to submit + immediately get a submission object back.

✅ This is the one we successfully ran.

fetch_submission.py

Fetches and prints a summary for a given sid:

calls al.submission.full(sid) (or equivalent)

prints state, completed timestamp, max_score, verdict, files list, results count, etc
Use this to poll/verify completion and to extract signals later for RiskProfile.

✅ This is the one we used to confirm completion.

ingest_sender.py

Asynchronous ingestion demo using the Ingest API:

submits files with a notification queue name (nq)

“fire-and-forget” style, doesn’t wait for completion

ingest_receiver.py

Pairs with ingest_sender.py:

listens/polls the notification queue

receives completion messages (so you don’t have to spam search/poll submission endpoints)

README.md

How to set up venv, install deps, configure .env, and run each script (submit/fetch/ingest sender/receiver).

structure.txt

Just notes about the demo structure (not required for runtime).

__pycache__/

Python bytecode cache (ignore).