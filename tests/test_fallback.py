from app.models import InsightRequest, ProductPeriod
from app.providers import InsightProvider
from app.service import create_insight


class BrokenProvider(InsightProvider):
    def generate(self, product_name, audience, metrics):
        raise ValueError("synthetic provider failure")


def test_invalid_provider_uses_labelled_fallback() -> None:
    request = InsightRequest(
        product_name="Synthetic Workspace",
        current=ProductPeriod(visitors=100, signups=20, activated_users=10, retained_users=5),
        previous=ProductPeriod(visitors=100, signups=20, activated_users=10, retained_users=5),
    )
    response = create_insight(request, BrokenProvider())
    assert response.insight.mode == "fallback"
    assert response.metrics.signup_rate == 20.0
