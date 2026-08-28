import json
from abc import ABC, abstractmethod

import httpx

from .models import MetricSnapshot, NarrativeInsight
from .prompts import SYSTEM_PROMPT_V1, build_context


class InsightProvider(ABC):
    @abstractmethod
    def generate(
        self, product_name: str, audience: str, metrics: MetricSnapshot
    ) -> NarrativeInsight:
        raise NotImplementedError


class MockProvider(InsightProvider):
    def generate(
        self, product_name: str, audience: str, metrics: MetricSnapshot
    ) -> NarrativeInsight:
        strongest = max(
            (metrics.signup_rate_change, "signup"),
            (metrics.activation_rate_change, "activation"),
            (metrics.retention_rate_change, "retention"),
            key=lambda pair: abs(pair[0]),
        )
        direction = "improved" if strongest[0] >= 0 else "declined"
        return NarrativeInsight(
            headline=f"{strongest[1].title()} {direction} in the current period",
            summary=(
                f"{product_name}'s {strongest[1]} rate changed by {abs(strongest[0]):.2f} "
                "percentage points. This describes correlation in the supplied aggregates, "
                "not cause."
            ),
            observations=[signal.replace("_", " ") for signal in metrics.signals],
            suggested_actions=[
                f"Review recent {strongest[1]} journey changes with the {audience} team",
                "Segment the metric before deciding on a product change",
            ],
            confidence="medium",
            mode="mock",
        )


class OpenAICompatibleProvider(InsightProvider):
    def __init__(self, base_url: str, model: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def generate(
        self, product_name: str, audience: str, metrics: MetricSnapshot
    ) -> NarrativeInsight:
        context = build_context(product_name, audience, metrics.model_dump())
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT_V1},
                    {"role": "user", "content": json.dumps(context)},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            },
            timeout=15,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = NarrativeInsight.model_validate_json(content)
        return parsed.model_copy(update={"mode": "provider"})
