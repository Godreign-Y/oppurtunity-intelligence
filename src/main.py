from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: We could verify DB connection here
    yield
    # Shutdown

app = FastAPI(
    title="Funding Intelligence Engine",
    description="API for collecting and processing funding events.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Funding Intelligence Engine API"}
