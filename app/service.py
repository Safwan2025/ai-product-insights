import logging

import httpx
from pydantic import ValidationError

from .metrics import calculate
from .models import InsightRequest, InsightResponse, NarrativeInsight
from .providers import InsightProvider, MockProvider

logger = logging.getLogger("ai-product-insights")


def fallback(_request: InsightRequest, _reason: str) -> NarrativeInsight:
    return NarrativeInsight(
        headline="Metrics are ready; narrative generation is unavailable",
        summary=(
            "The deterministic product metrics were calculated successfully. "
            "The narrative provider did not return a valid response."
        ),
        observations=["Validated metrics remain available in this response"],
        suggested_actions=["Review the metric changes directly before taking action"],
        confidence="high",
        mode="fallback",
    )


def create_insight(
    request: InsightRequest, provider: InsightProvider | None = None
) -> InsightResponse:
    metrics = calculate(request)
    selected_provider = provider or MockProvider()
    for attempt in range(2):
        try:
            insight = selected_provider.generate(request.product_name, request.audience, metrics)
            return InsightResponse(metrics=metrics, insight=insight)
        except (httpx.HTTPError, KeyError, TypeError, ValidationError, ValueError) as error:
            logger.warning(
                "provider_attempt_failed attempt=%s error_type=%s",
                attempt + 1,
                type(error).__name__,
            )
    return InsightResponse(metrics=metrics, insight=fallback(request, "provider_invalid"))
