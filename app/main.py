from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1.endpoints.leads import router as leads_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# Include API routers
app.include_router(leads_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to Lead Agent API", "docs": "/docs"}