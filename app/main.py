from fastapi import FastAPI

from app.modules.auth import router as auth_router

app = FastAPI(
    title="FlowTask API",
    description="A smart task management API",
    version="0.1.0",
)

app.include_router(auth_router.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "FlowTask API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
