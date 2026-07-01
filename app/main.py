from fastapi import FastAPI
from app.routers import auth, services, incidents, subscribers, status  # add status

app = FastAPI(title="StatusNest Auth Service")

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(incidents.router)
app.include_router(subscribers.router)
app.include_router(status.router)   # add this

@app.get("/health")
def health():
    return {"status": "ok"}