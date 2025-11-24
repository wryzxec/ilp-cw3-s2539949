from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.controller.drone_controller import router as drone_router

app = FastAPI()

class Health(BaseModel):
    status: str

BASE_URL = "http://localhost:8080"

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/actuator/health", response_model=Health)
def health():
    return Health(status="UP")

@app.get("/")
def get_map():
    return FileResponse("static/map.html")

app.include_router(drone_router)

for route in app.routes:
    print("ROUTE:", route.path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )