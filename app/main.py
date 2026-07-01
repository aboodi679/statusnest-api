from fastapi import FastAPI
from app.routers import auth
from app.routers import services, incidents, subscribers

app = FastAPI(title="StatusNest Auth Service")

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(incidents.router)
app.include_router(subscribers.router)


@app.get("/health")
def health():
    return {"status": "ok"}
