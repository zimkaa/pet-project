import uvicorn

from src.main import app


if __name__ == "__main__":
    uvicorn.run(app, port=9000, log_level="info")
