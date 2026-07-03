from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aws_xray_sdk.core import xray_recorder, patch_all
from app.routers import status

patch_all()
xray_recorder.configure(service="statusnest-status", daemon_address="127.0.0.1:2000")

app = FastAPI(title="StatusNest Status Page Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def xray_middleware(request, call_next):
    segment = xray_recorder.begin_segment(name="statusnest-status")
    try:
        response = await call_next(request)
        segment.put_http_meta("status", response.status_code)
        return response
    except Exception as e:
        segment.add_exception(e, True)
        raise
    finally:
        xray_recorder.end_segment()

app.include_router(status.router)

@app.get("/health")
def health():
    return {"status": "ok"}
