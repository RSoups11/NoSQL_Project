from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.proteins import router as proteins_router
from routers.graph import router as graph_router
from routers.annotation import router as annotation_router

app = FastAPI(title="NoSQL Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proteins_router)
app.include_router(graph_router)
app.include_router(annotation_router)

@app.get("/")
async def root():
    return {
        "message": "API running"
    }
