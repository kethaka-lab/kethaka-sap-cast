# C4 forecast service. Run locally with:

# Command: uv run uvicorn kethaka_sap_cast.api:app --reload
# Interactive docs: http://127.0.0.1:8000/docs

from fastapi import FastAPI

app = FastAPI(
    title="Kethaka C4 - Sap Yield Forecast",
    description="7-day daily sap forecast for the estate, with replay mode for verification.",
    version="0.1.0",
)


@app.get("/health", tags=["service"])
def health() -> dict:
    """Liveness check used by the common backend before forwarding requests."""
    return {"status": "ok", "service": "c4-forecast"}