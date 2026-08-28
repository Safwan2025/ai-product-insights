SYSTEM_PROMPT_V1 = """You explain pre-calculated SaaS product metrics.
Never recalculate metrics, invent causes, or claim certainty about causation.
Separate observation from recommendation. Return only the requested JSON schema.
Keep the language concise, specific and useful to the named audience."""


def build_context(
    product_name: str, audience: str, metrics: dict[str, object]
) -> dict[str, object]:
    return {
        "prompt_version": "product-insights-v1",
        "product_name": product_name,
        "audience": audience,
        "validated_metrics": metrics,
        "instruction": "Explain the signals and suggest investigation steps, not conclusions.",
    }
