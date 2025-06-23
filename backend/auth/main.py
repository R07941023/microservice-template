from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"service": "auth", "status": "ok"}