from fastapi import FastAPI

app = FastAPI(
    title="FlowTask API",
    description="A smart task management API",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "FlowTask API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
