from fastapi import FastAPI, UploadFile
from .fsm import run_fsm

app = FastAPI(title="SentinelLine Agent")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/submit")
async def submit(file: UploadFile):
    content = await file.read()
    result = run_fsm(file.filename, content)
    return result
