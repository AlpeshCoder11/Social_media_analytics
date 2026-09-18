import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the app module can be found
sys.path.append(str(Path(__file__).resolve().parent))

from app.api.routes import router as network_router

app = FastAPI(
    title="SIH Social Media Analytics API",
    description="Backend API for the SIH Problem Statement 26152 Dashboard",
    version="1.0.0"
)

# Allow frontend dashboard to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the network analytics endpoints
app.include_router(network_router)

@app.get("/")
def read_root():
    return {"message": "SIH Analytics API is running. Visit /docs for the interactive API documentation."}

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting SIH Analytics FastAPI Server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)