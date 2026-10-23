"""Marketplace listing model for TekunoAI Agent Universe.

Stdlib only. A Listing is what a seller agent is selling and what a
buyer agent discovers, compares and negotiates over.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Listing:
    id: str
    title: str
    seller_id: str
    list_price: float
    floor_price: float
    category: str = "general"
    description: str = ""
    currency: str = "USD"
    condition: str = "new"
    quantity: int = 1
    tags: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.list_price <= 0:
            raise ValueError("list_price must be positive")
        if self.floor_price <= 0:
            raise ValueError("floor_price must be positive")
        if self.floor_price > self.list_price:
            raise ValueError("floor_price cannot exceed list_price")
        if self.quantity < 1:
            raise ValueError("quantity must be at least 1")

    @property
    def margin_range(self) -> float:
        """Negotiable range between floor and list price."""
        return round(self.list_price - self.floor_price, 2)

    def summary(self) -> str:
        return (
            f"{self.title} [{self.id}] - {self.currency} {self.list_price:.2f} "
            f"(floor {self.currency} {self.floor_price:.2f}, {self.condition}, "
            f"category: {self.category}, seller: {self.seller_id})"
        )
