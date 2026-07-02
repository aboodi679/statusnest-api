from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, services, incidents, subscribers, status

app = FastAPI(title="StatusNest Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(incidents.router)
app.include_router(subscribers.router)
app.include_router(status.router)

@app.get("/health")
def health():
    return {"status": "ok"}