from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ProductPeriod(BaseModel):
    visitors: int = Field(ge=0)
    signups: int = Field(ge=0)
    activated_users: int = Field(ge=0)
    retained_users: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_funnel(self) -> "ProductPeriod":
        if self.signups > self.visitors:
            raise ValueError("signups cannot exceed visitors")
        if self.activated_users > self.signups:
            raise ValueError("activated_users cannot exceed signups")
        if self.retained_users > self.activated_users:
            raise ValueError("retained_users cannot exceed activated_users")
        return self


class InsightRequest(BaseModel):
    product_name: str = Field(min_length=2, max_length=80)
    current: ProductPeriod
    previous: ProductPeriod
    audience: Literal["product", "engineering", "leadership"] = "product"


class MetricSnapshot(BaseModel):
    signup_rate: float
    activation_rate: float
    retention_rate: float
    signup_rate_change: float
    activation_rate_change: float
    retention_rate_change: float
    signals: list[str]


class NarrativeInsight(BaseModel):
    headline: str = Field(min_length=5, max_length=140)
    summary: str = Field(min_length=10, max_length=600)
    observations: list[str] = Field(min_length=1, max_length=5)
    suggested_actions: list[str] = Field(min_length=1, max_length=4)
    confidence: Literal["low", "medium", "high"]
    mode: Literal["mock", "provider", "fallback"]


class InsightResponse(BaseModel):
    metrics: MetricSnapshot
    insight: NarrativeInsight
    disclaimer: str = "Generated from synthetic or user-supplied aggregates; verify before acting."
