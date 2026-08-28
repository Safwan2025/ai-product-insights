import os

from fastapi import FastAPI

from .models import InsightRequest, InsightResponse
from .providers import MockProvider, OpenAICompatibleProvider
from .service import create_insight

app = FastAPI(title="AI Product Insights", version="1.0.0")


def provider_from_environment():
    if os.getenv("INSIGHTS_MODE", "mock") == "provider" and os.getenv("AI_API_KEY"):
        return OpenAICompatibleProvider(
            os.getenv("AI_BASE_URL", "https://api.openai.com/v1"),
            os.getenv("AI_MODEL", "gpt-5-mini"),
            os.environ["AI_API_KEY"],
        )
    return MockProvider()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": os.getenv("INSIGHTS_MODE", "mock")}


@app.post("/v1/insights", response_model=InsightResponse)
def insights(request: InsightRequest) -> InsightResponse:
    return create_insight(request, provider_from_environment())
