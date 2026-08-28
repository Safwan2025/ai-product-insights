from app.metrics import calculate
from app.models import InsightRequest, ProductPeriod


def request() -> InsightRequest:
    return InsightRequest(
        product_name="Synthetic Workspace",
        current=ProductPeriod(visitors=1000, signups=200, activated_users=120, retained_users=72),
        previous=ProductPeriod(visitors=1000, signups=150, activated_users=75, retained_users=45),
    )


def test_metrics_are_deterministic() -> None:
    metrics = calculate(request())
    assert metrics.signup_rate == 20.0
    assert metrics.activation_rate == 60.0
    assert metrics.retention_rate == 60.0
    assert metrics.signup_rate_change == 5.0
    assert metrics.activation_rate_change == 10.0


def test_mock_mode_needs_no_api_key() -> None:
    from app.service import create_insight

    response = create_insight(request())
    assert response.insight.mode == "mock"
    assert response.metrics.activation_rate == 60.0
