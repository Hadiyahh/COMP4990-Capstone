# SentinelLine + Assemblyline: Full Code Truth Review

Date: 2026-03-24
Scope reviewed from current code in workspace.

---

## A) Beginner-friendly explanation

## What happens when you start the system?

There are two different stacks in your workspace:

1. SentinelLine app stack
- File: COMP4990-Capstone/docker-compose.yml:1
- Starts only 2 containers: `agent` and `dashboard`.
- It does **not** start Assemblyline itself.
- The agent expects Assemblyline to already exist at `https://host.docker.internal` (COMP4990-Capstone/docker-compose.yml:15).

2. Assemblyline platform stack
- File: deployments/assemblyline/docker-compose.yaml:1
- Starts the full Assemblyline ecosystem (Elasticsearch, Redis, UI, socket, ingester, dispatcher, workflow, etc.) using profiles and shared templates.

So in plain words:
- SentinelLine is your custom app (upload API + FSM + logs + Streamlit dashboard).
- Assemblyline is external malware analysis infrastructure that SentinelLine calls.

## What happens when you submit a file?

1. Request enters SentinelLine FastAPI `POST /submit`.
- File: COMP4990-Capstone/agent/app/main.py:11

2. File bytes are read, then FSM starts.
- File: COMP4990-Capstone/agent/app/main.py:20
- File: COMP4990-Capstone/agent/app/main.py:21

3. FSM runs states in strict order:
- received -> triage -> route -> submit -> wait -> score -> respond
- File: COMP4990-Capstone/agent/app/fsm.py:47
- File: COMP4990-Capstone/agent/app/fsm.py:53
- File: COMP4990-Capstone/agent/app/fsm.py:66
- File: COMP4990-Capstone/agent/app/fsm.py:80
- File: COMP4990-Capstone/agent/app/fsm.py:91
- File: COMP4990-Capstone/agent/app/fsm.py:102
- File: COMP4990-Capstone/agent/app/fsm.py:115

4. During states, SentinelLine sends file to Assemblyline `/api/v4/submit/`, then polls for completion, then scores and returns recommendation.

5. Every state writes JSONL audit events to shared log directory.
- File: COMP4990-Capstone/agent/app/auditlog.py:17

6. Dashboard simply reads all JSONL lines and displays them.
- File: COMP4990-Capstone/dashboard/app.py:7
- File: COMP4990-Capstone/dashboard/app.py:13

## Real entry points

- SentinelLine runtime entrypoint in container:
  - `uvicorn app.main:app`
  - File: COMP4990-Capstone/agent/Dockerfile:11
- SentinelLine API entry function:
  - `submit(file)`
  - File: COMP4990-Capstone/agent/app/main.py:12
- FSM orchestration entry:
  - `run_fsm(filename, content)`
  - File: COMP4990-Capstone/agent/app/fsm.py:32
- Dashboard runtime entrypoint:
  - `streamlit run app.py`
  - File: COMP4990-Capstone/dashboard/Dockerfile:10

---

## 1) Overall flow (start to finish)

### Start flow

### If you run SentinelLine compose
1. `agent` container starts (COMP4990-Capstone/docker-compose.yml:4).
2. `dashboard` container starts (COMP4990-Capstone/docker-compose.yml:17).
3. Both mount `./data/logs` to `/logs` (COMP4990-Capstone/docker-compose.yml:9,22).
4. Agent uses env vars for Assemblyline URL/creds (COMP4990-Capstone/docker-compose.yml:10-15).

### If you run Assemblyline compose
1. Dependency anchors define startup constraints (deployments/assemblyline/docker-compose.yaml:1-35).
2. Redis/Elasticsearch/minio and full-profile observability services start as configured.
3. Core services start from shared templates in common/core.yaml.

### Submit flow
1. POST `/submit` receives file (COMP4990-Capstone/agent/app/main.py:11-12).
2. `run_fsm()` runs pipeline (COMP4990-Capstone/agent/app/main.py:21).
3. FSM transitions through all states and logs each stage (COMP4990-Capstone/agent/app/fsm.py:44-124).
4. Final JSON response is returned by API endpoint (COMP4990-Capstone/agent/app/main.py:22).

---

## 2) Docker / setup

## Which docker-compose or YAML files matter?

Primary SentinelLine files:
- COMP4990-Capstone/docker-compose.yml
- COMP4990-Capstone/agent/Dockerfile
- COMP4990-Capstone/dashboard/Dockerfile

Assemblyline deployment files:
- deployments/assemblyline/docker-compose.yaml
- deployments/assemblyline/common/core.yaml
- deployments/assemblyline/common/elasticsearch.yaml
- deployments/assemblyline/common/nginx.yaml

## What each service/container does (simple words)

SentinelLine compose:
- `agent`: FastAPI API that runs FSM and calls Assemblyline.
- `dashboard`: Streamlit UI that displays JSONL logs.

Assemblyline compose (high-level groups):
- Storage/indexing: `minio`, `elasticsearch_*`, `redis`.
- Observability full profile: `kibana`, `apm_server`, `filebeat`, `metricbeat`, `metrics`.
- Core processing: `alerter`, `archiver`, `expiry`, `heartbeat`, `plumber`, `statistics`, `workflow`, `scaler`, `updater`, `dispatcher`, `ingester`.
- APIs/UI edges: `service_server`, `ui`, `socketio`, `frontend`, `nginx_*`.

## Assemblyline infrastructure vs SentinelLine app

Assemblyline infrastructure (deployment files under deployments/assemblyline):
- Elasticsearch, Redis, Minio, core workers, UI/socket, nginx proxy, etc.

Your SentinelLine app (COMP4990-Capstone):
- Custom FastAPI agent, FSM logic, scoring, route logic, audit logger, Streamlit dashboard.

## What depends on what

In Assemblyline compose:
- Many services depend on elasticsearch health anchors (deployments/assemblyline/docker-compose.yaml:1-24).
- In full profile, Kibana depends on Elasticsearch + kb_setup completion (deployments/assemblyline/docker-compose.yaml:77-82).
- UI/socket/nginx depend on relevant services depending on profile (deployments/assemblyline/docker-compose.yaml:188-214, 435-450).
- `service_server`, `ui`, `socketio` also depend on elasticsearch+redis anchor via profile variants (deployments/assemblyline/docker-compose.yaml:401-450).

In SentinelLine compose:
- No explicit `depends_on` between agent/dashboard.
- Both rely on shared host logs directory.

---

## 3) Code flow by important function (does/called by/returns/next)

## COMP4990-Capstone/agent/app/main.py

### `submit(file)` at line 12
- Does: receives uploaded file, reads bytes, starts FSM.
- Called by: FastAPI route `POST /submit`.
- Returns: JSON response containing FSM output or error.
- Calls next: `run_fsm(...)` in fsm.py line 32.

## COMP4990-Capstone/agent/app/fsm.py

### `run_fsm(filename, content)` at line 32
- Does: orchestrates full pipeline and logs each stage.
- Called by: `main.submit()`.
- Returns: final response dict from `handle_respond()`.
- Calls next in sequence:
  - `handle_received()`
  - `handle_triage()`
  - `handle_route()`
  - `handle_submit()`
  - `handle_wait()`
  - `handle_score()`
  - `handle_respond()`

### `log_state_transition(...)` at line 20
- Does: appends in-memory audit trail to `context.audit_trail`.
- Called by: `run_fsm()` after each stage.
- Returns: nothing.
- Calls next: none.

## COMP4990-Capstone/agent/app/states/received.py

### `handle_received(...)` at line 25
- Does: generates file_id + sha256 hash, initializes StateContext with status=`triage`.
- Called by: `run_fsm()`.
- Returns: `StateContext`.
- Calls next: returns to FSM, then FSM calls `handle_triage()`.

## COMP4990-Capstone/agent/app/states/triage.py

### `handle_triage(context)` at line 196
- Does: computes entropy, detects file type, checks YARA, computes initial risk score.
- Called by: `run_fsm()`.
- Returns: updated `StateContext` with `risk_profile`, status=`route`.
- Calls next internally:
  - `calculate_entropy()` line 35
  - `detect_file_type()` line 59
  - `check_yara_rules()` line 90
  - `query_external_apis()` line 176 (currently stubbed)
- Then FSM calls `handle_route()`.

## COMP4990-Capstone/agent/app/states/route.py

### `handle_route(context)` at line 40
- Does: decides FAST/DEEP/HUMAN_REVIEW; sets `routing_rationale`; builds `analysis_config`.
- Called by: `run_fsm()`.
- Returns: updated `StateContext` with status=`submit`.
- Calls next internally: `determine_analysis_config()` line 120.
- Then FSM calls `handle_submit()`.

### `determine_analysis_config(...)` at line 120
- Does: maps route to `timeout`, `analysis_type`, `deep_scan`, `extra_services`.
- Called by: `handle_route()`.
- Returns: analysis config dict.
- Calls next: none.

## COMP4990-Capstone/agent/app/states/submit.py

### `handle_submit(context)` at line 172
- Does: sends file to Assemblyline and stores `submission_id`.
- Called by: `run_fsm()`.
- Returns: updated `StateContext` with status=`wait`.
- Calls next: `submit_to_assemblyline()` line 98.

### `submit_to_assemblyline(...)` at line 98
- Does: creates authenticated session, posts file to Assemblyline submit endpoint.
- Called by: `handle_submit()`.
- Returns: `submission_id`.
- Calls next internally:
  - `_create_authenticated_session()` line 59
  - `session.post(...)` to `/api/v4/submit/` line 145

## COMP4990-Capstone/agent/app/states/wait.py

### `handle_wait(context, timeout=...)` at line 163
- Does: polls submission until complete, then pulls full analysis report.
- Called by: `run_fsm()`.
- Returns: updated `StateContext` with `analysis_report`, status=`score`.
- Calls next internally:
  - `get_submission_status()` line 103
  - `get_analysis_report()` line 129
- Then FSM calls `handle_score()`.

## COMP4990-Capstone/agent/app/states/score.py

### `handle_score(context)` at line 144
- Does: parses report, computes confidence, normalizes final risk score.
- Called by: `run_fsm()`.
- Returns: updated `StateContext` with score/confidence/status=`respond`.
- Calls next internally:
  - `parse_assemblyline_score()` line 25
  - `calculate_confidence_score()` line 68
  - `normalize_risk_score()` line 118
- Then FSM calls `handle_respond()`.

## COMP4990-Capstone/agent/app/states/respond.py

### `handle_respond(context)` at line 122
- Does: chooses recommendation and builds final report + dashboard_update payload.
- Called by: `run_fsm()`.
- Returns: final response dict with `recommendation`, `final_report`, `dashboard_update`, `status`.
- Calls next internally:
  - `determine_recommendation()` line 24
  - `build_final_report()` line 48
  - `build_dashboard_update()` line 94

## COMP4990-Capstone/agent/app/auditlog.py

### `log_event(state, data, trace_id=None)` at line 5
- Does: appends one JSON line to per-trace log file.
- Called by: `run_fsm()`.
- Returns: `trace_id`.
- Calls next: none.

## COMP4990-Capstone/dashboard/app.py

Top-level script body
- Does: discovers all `/logs/*.jsonl`, reads every line, displays each JSON object.
- Called by: Streamlit runtime.
- Returns: none.
- Calls next: none.

---

## 4) SentinelLine FSM exact path for one submitted file

1. Request enters at `POST /submit`.
- COMP4990-Capstone/agent/app/main.py:11

2. File read.
- COMP4990-Capstone/agent/app/main.py:20

3. FSM starts.
- COMP4990-Capstone/agent/app/main.py:21
- COMP4990-Capstone/agent/app/fsm.py:32

4. `received` happens.
- Call site: COMP4990-Capstone/agent/app/fsm.py:47
- Handler: COMP4990-Capstone/agent/app/states/received.py:25

5. `triage` happens.
- Call site: COMP4990-Capstone/agent/app/fsm.py:53
- Handler: COMP4990-Capstone/agent/app/states/triage.py:196

6. `route` happens.
- Call site: COMP4990-Capstone/agent/app/fsm.py:66
- Handler: COMP4990-Capstone/agent/app/states/route.py:40

7. `submit` happens.
- Call site: COMP4990-Capstone/agent/app/fsm.py:80
- Handler: COMP4990-Capstone/agent/app/states/submit.py:172

8. `wait` happens.
- Call site: COMP4990-Capstone/agent/app/fsm.py:91
- Handler: COMP4990-Capstone/agent/app/states/wait.py:163

9. `score` happens.
- Call site: COMP4990-Capstone/agent/app/fsm.py:102
- Handler: COMP4990-Capstone/agent/app/states/score.py:144

10. `respond` happens.
- Call site: COMP4990-Capstone/agent/app/fsm.py:115
- Handler: COMP4990-Capstone/agent/app/states/respond.py:122

11. Final response returned.
- COMP4990-Capstone/agent/app/fsm.py:124
- COMP4990-Capstone/agent/app/main.py:22

---

## 5) Route logic (FAST / DEEP / HUMAN_REVIEW)

Decision code location:
- COMP4990-Capstone/agent/app/states/route.py:40-117

Conditions for HUMAN_REVIEW:
- `has_definitive` true (line 70)
- `yara_hit_count >= 4` (line 73)
- `risk_score >= 75` (line 76)
- `entropy > 7.5` (line 79)
- file type contains `unknown` (line 82)

Conditions for DEEP:
- `1 <= yara_hit_count <= 3` (line 88)
- `25 <= risk_score < 75` (line 91)
- `6.0 <= entropy <= 7.5` (line 94)

FAST fallback:
- else block when none of above matched (line 100)

Attached fields after decision:
- `routing_decision` (line 112)
- `routing_rationale` (line 113)
- `analysis_config` from `determine_analysis_config` (line 109/114)
- `status = "submit"` (line 115)

Important truth check:
- The `ROUTING_RULES` dict at route.py:20 is **not used** in decision execution.
- Actual behavior comes from explicit if/elif blocks at lines 68-104.

Does route map to real Assemblyline profiles?
- In this SentinelLine code: **No explicit Assemblyline profile selection is implemented**.
- It maps to app-side `analysis_config` fields (`timeout`, `deep_scan`, `extra_services`) only.
- `analysis_type` is set in route config, but not included in submit payload fields actually sent.

---

## 6) Assemblyline submission (exact code and payload)

Exact send-to-Assemblyline code:
- Function: `submit_to_assemblyline(...)`
- File: COMP4990-Capstone/agent/app/states/submit.py:98

Endpoint used:
- `/api/v4/submit/`
- Built at submit.py:125

Auth behavior:
- Prefers login session if username/password present (submit.py:62-83).
- Falls back to API key header probe (submit.py:85-93).

HTTP payload sent:
- File part named `bin`: submit.py:131-133
- Form field `json` string containing:
  - `timeout`
  - `deep_scan`
  - `extra_services`
- Built at submit.py:136-142

Submission behavior controls currently used:
- Comes from route `analysis_config` (route.py:109-151).
- Sent fields actually used by submit function:
  - timeout
  - deep_scan
  - extra_services
- `analysis_type` exists in route config but is **not sent** (not present in submit payload lines 136-142).

Selected services currently used?
- In FSM submit path, there is **no `services.selected` field sent**.
- In separate api_demo scripts, selected services are used (ingest_sender.py:52 and submit_demo.py:26), but that is not the same execution path as app FSM.

---

## 7) Service/profile mapping truth (FAST / DEEP / HUMAN_REVIEW)

Based on current FSM code:

FAST
- timeout=60, deep_scan=False, extra_services=[]
- route.py:131-136

DEEP
- timeout=600, deep_scan=True, extra_services=["yara", "pe_recommendations"]
- route.py:137-142

HUMAN_REVIEW
- timeout=1800, deep_scan=True, extra_services=["yara", "pe_recommendations", "code_analysis"]
- route.py:143-148

Not explicitly implemented (important)
- No code routes a file to a different Assemblyline compose profile (`minimal`/`full`) from SentinelLine.
- No explicit escalation workflow to a human reviewer queue/system exists in code.
- HUMAN_REVIEW is currently a decision label plus longer/deeper submit settings and recommendation logic.

---

## 8) Audit/reporting

Where logs are written:
- `LOG_DIR` env var (default `./logs`) in auditlog.py:3
- Directory creation auditlog.py:16
- JSONL append write auditlog.py:17

What JSONL files are produced:
- One file per trace id: `{LOG_DIR}/{trace_id}.jsonl`
- auditlog.py:17

What each JSONL entry stores:
- `trace_id`
- `state`
- `data`
- `timestamp`
- auditlog.py:9-14

How dashboard reads logs:
- Finds all `/logs/*.jsonl` (dashboard/app.py:7)
- Opens each file and parses every line as JSON (dashboard/app.py:11-13)
- Displays as Streamlit JSON blocks.

---

## 9) Gaps / truth check (brutally honest)

### Intended vs actual

1. "SentinelLine starts everything"
- Actual: SentinelLine compose starts only `agent` and `dashboard`.
- Assemblyline must be started separately or already reachable.
- Evidence: COMP4990-Capstone/docker-compose.yml:3-22

2. "Route profiles map to Assemblyline platform profiles"
- Actual: They do not map to Assemblyline compose profiles in this code.
- Route maps only to timeout/deep_scan/extra_services in app logic.
- Evidence: route.py:120-151 + submit.py:136-142

3. "ROUTING_RULES controls decisions"
- Actual: `ROUTING_RULES` is not used by runtime routing logic.
- Real logic is explicit if/elif chain.
- Evidence: route.py:20 and route.py:68-104

4. "HUMAN_REVIEW triggers a separate human process"
- Actual: No explicit human workflow integration found in current code.
- It is a route label and different config values.

5. "Explain route message is always accurate"
- Actual: `explain_route` only has special text for DEEP; all non-DEEP routes get FAST-style message.
- HUMAN_REVIEW currently gets "fast analysis" wording in this helper.
- Evidence: explain.py:1-4

6. "Scoring reads guaranteed report schema"
- Actual: Scoring assumes specific keys (`derived.score`, `results`, `result.tags`).
- If report shape differs, behavior may degrade.
- Evidence: score.py:41,50,46

7. "Route analysis_type affects submission"
- Actual: `analysis_type` is generated but not sent in payload.
- Evidence: route.py:133/139/145 vs submit.py:136-142

8. "API key always used"
- Actual: if username/password exist, session login path is attempted first.
- Evidence: submit.py:62-83

9. "Dashboard shows computed final reports only"
- Actual: Dashboard renders whatever JSONL entries exist, line by line.
- Evidence: dashboard/app.py:7-13

10. Security risk currently present
- Hardcoded API key in compose file.
- Evidence: COMP4990-Capstone/docker-compose.yml:12

If you expected behavior not listed above, I cannot confirm from the current code.

---

## 10) Technical trace with file + function + line numbers

### Start and API entry
1. SentinelLine containers defined: COMP4990-Capstone/docker-compose.yml:3
2. Agent runtime command: COMP4990-Capstone/agent/Dockerfile:11
3. FastAPI endpoint `/submit`: COMP4990-Capstone/agent/app/main.py:11
4. FSM handoff: COMP4990-Capstone/agent/app/main.py:21

### FSM chain
1. `run_fsm`: COMP4990-Capstone/agent/app/fsm.py:32
2. `handle_received`: COMP4990-Capstone/agent/app/fsm.py:47 -> states/received.py:25
3. `handle_triage`: COMP4990-Capstone/agent/app/fsm.py:53 -> states/triage.py:196
4. `handle_route`: COMP4990-Capstone/agent/app/fsm.py:66 -> states/route.py:40
5. `handle_submit`: COMP4990-Capstone/agent/app/fsm.py:80 -> states/submit.py:172
6. `handle_wait`: COMP4990-Capstone/agent/app/fsm.py:91 -> states/wait.py:163
7. `handle_score`: COMP4990-Capstone/agent/app/fsm.py:102 -> states/score.py:144
8. `handle_respond`: COMP4990-Capstone/agent/app/fsm.py:115 -> states/respond.py:122
9. Return response: COMP4990-Capstone/agent/app/fsm.py:124

### Assemblyline submit/wait internals
1. Submit endpoint built: states/submit.py:125
2. File payload field: states/submit.py:131
3. JSON payload fields: states/submit.py:137-140
4. POST happens: states/submit.py:145
5. Poll status endpoint: states/wait.py:116
6. Pull full report endpoint options: states/wait.py:143-146

### Logging and dashboard
1. FSM log calls per state: fsm.py:49,59,72,84,95,107,119
2. JSONL write: auditlog.py:17
3. Dashboard reads all logs: dashboard/app.py:7-13

### api_demo separate path (not FSM path)
- Config: api_demo/config.py:9-28
- Client: api_demo/client.py:7-16
- Async ingest: api_demo/ingest_sender.py:61
- Queue receive + fetch: api_demo/ingest_receiver.py:18,43
- Manual fetch by SID: api_demo/fetch_submission.py:17

---

## Top 5 files to understand first

1. COMP4990-Capstone/agent/app/fsm.py
- Central orchestrator for full file lifecycle.

2. COMP4990-Capstone/agent/app/states/route.py
- Core decision engine for FAST/DEEP/HUMAN_REVIEW.

3. COMP4990-Capstone/agent/app/states/submit.py
- Real integration point to Assemblyline API submit endpoint.

4. COMP4990-Capstone/agent/app/states/wait.py
- Polling/report retrieval behavior and completion logic.

5. COMP4990-Capstone/docker-compose.yml
- Defines what actually starts in your SentinelLine stack.

---

## C) Presentation version (short, say out loud)

"SentinelLine is a thin orchestration layer in front of Assemblyline. When I submit a file to `/submit`, FastAPI reads the bytes and runs a 7-stage FSM: received, triage, route, submit, wait, score, respond. The submit stage sends the file to Assemblyline `/api/v4/submit/`, the wait stage polls until complete, score calculates risk and confidence, and respond returns recommendation plus report. Every stage is logged to per-trace JSONL files, and the Streamlit dashboard just reads and displays those logs. Important truth: in current code, FAST/DEEP/HUMAN_REVIEW only change timeout/deep_scan/extra_services; they do not switch Assemblyline compose profiles or trigger a real human-review workflow." 

---

## One-page architecture summary

System layers
1. Ingress/API layer
- FastAPI service receives upload requests (`POST /submit`).

2. Orchestration layer
- FSM coordinates deterministic stage transitions and state logging.

3. Analysis integration layer
- Submit state authenticates and sends multipart request to Assemblyline submit endpoint.
- Wait state polls submission status and fetches report payload.

4. Decision layer
- Route chooses path based on triage-derived risk indicators.
- Score translates Assemblyline report signals into normalized risk + confidence.
- Respond creates final recommendation and response structures.

5. Observability layer
- Audit logger writes JSONL events per trace.
- Dashboard reads JSONL files and renders entries.

Runtime topology
- SentinelLine compose: `agent` + `dashboard` only.
- Assemblyline stack: separate deployment compose with Elasticsearch/Redis/core workers/UI/etc.
- SentinelLine depends on Assemblyline URL/credentials via env vars.

Key control data
- StateContext object carries everything through pipeline.
- Route attaches analysis_config.
- Submit sends timeout/deep_scan/extra_services + file.
- Wait enriches context with analysis_report.
- Score/Respond finalize risk and recommendation.

Current behavior boundaries
- Real implemented behavior: deterministic FSM + Assemblyline submit/poll + JSONL auditing.
- Not fully implemented from architecture intent: explicit human-review workflow, route-to-compose-profile mapping, external threat intel enrichment beyond stub.
