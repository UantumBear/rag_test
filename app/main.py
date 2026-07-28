from fastapi import FastAPI, status

app = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK)
def health() -> dict[str, str]:
    """Return the application's health status."""
    return {"status": "ok"}
