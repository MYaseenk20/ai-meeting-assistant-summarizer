from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.router import router

app = FastAPI(
    title="AI Meeting Summarizer",
    description="Air Meeting Summarizer",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/", tags=["api"])
async def root():
    return {"status": "ok", "message": "AI Financial Research API is running."}