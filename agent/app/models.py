from pydantic import BaseModel

class Decision(BaseModel):
    trace_id: str
    route: str
    explanation: str
