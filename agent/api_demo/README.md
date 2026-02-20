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

---

If you want, paste:
1) your `submit_demo.py` output **once**  
or  
2) one queue message from `ingest_receiver.py`  
and I’ll tell you the exact key path for SID + where verdict/tags live in your version so your capstone write-up is precise.
::contentReference[oaicite:0]{index=0}