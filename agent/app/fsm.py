from .auditlog import log_event
from .explain import explain_route

def run_fsm(filename: str, content: bytes):
    trace_id = log_event("RECEIVED", {"file": filename})

    # TRIAGE (simple rule)
    suspicious = filename.endswith(".bin")

    log_event("TRIAGE", {"suspicious": suspicious}, trace_id)

    route = "DEEP" if suspicious else "FAST"
    explanation = explain_route(route, filename)

    log_event("ROUTE", {"route": route}, trace_id)

    return {
        "trace_id": trace_id,
        "route": route,
        "explanation": explanation
    }
