from fastapi import FastAPI
import datetime
import uvicorn

app = FastAPI()


@app.get("/time")
def get_server_time():
    """Endpoint yang mengembalikan waktu server dalam UTC."""
    return {
        "server_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "timezone": "UTC",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
