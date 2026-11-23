from fastapi import FastAPI

from app.routes.benchmark_routes import router as benchmark_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="EcoAI Benchmark",
    description="A platform for evaluating AI models based on performance and sustainability.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to EcoAI Benchmark!",
        "status": "Backend is running successfully"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(benchmark_router)