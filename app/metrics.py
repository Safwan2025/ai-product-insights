from .models import InsightRequest, MetricSnapshot, ProductPeriod


def rate(numerator: int, denominator: int) -> float:
    return round((numerator / denominator * 100) if denominator else 0.0, 2)


def period_rates(period: ProductPeriod) -> tuple[float, float, float]:
    return (
        rate(period.signups, period.visitors),
        rate(period.activated_users, period.signups),
        rate(period.retained_users, period.activated_users),
    )


def calculate(request: InsightRequest) -> MetricSnapshot:
    current = period_rates(request.current)
    previous = period_rates(request.previous)
    changes = tuple(round(now - before, 2) for now, before in zip(current, previous, strict=True))
    labels = ("signup", "activation", "retention")
    signals = []
    for label, change in zip(labels, changes, strict=True):
        if abs(change) >= 5:
            direction = "increased" if change > 0 else "decreased"
            signals.append(f"{label}_rate_{direction}_by_{abs(change):.2f}_points")
    if not signals:
        signals.append("no_material_rate_change")
    return MetricSnapshot(
        signup_rate=current[0],
        activation_rate=current[1],
        retention_rate=current[2],
        signup_rate_change=changes[0],
        activation_rate_change=changes[1],
        retention_rate_change=changes[2],
        signals=signals,
    )
