from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from backend.api.upload import router as upload_router
from backend.api.dashboard import router as dashboard_router
# from backend.api.comparison import router as comparison_router
# from backend.api.ai import router as ai_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(upload_router)
app.include_router(dashboard_router)
# app.include_router(comparison_router)
# app.include_router(ai_router)

