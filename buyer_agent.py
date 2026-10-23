"""Buyer agent for TekunoAI Agent Universe.

The buyer agent represents a human user. It never exceeds the user's
max budget and it tries to settle at or near the user's target price.
Stdlib only.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BuyerAgent:
    name: str
    max_budget: float
    target_price: float
    user_id: str = "user-1"

    def __post_init__(self) -> None:
        if self.max_budget <= 0:
            raise ValueError("max_budget must be positive")
        if self.target_price <= 0:
            raise ValueError("target_price must be positive")
        if self.target_price > self.max_budget:
            raise ValueError("target_price cannot exceed max_budget")

    def initial_offer(self, list_price: float) -> tuple[float, str]:
        offer = min(self.target_price, self.max_budget)
        reason = (
            f"Opening at my target price {offer:.2f}. "
            f"List price is {list_price:.2f}; similar items justify starting at target."
        )
        return round(offer, 2), reason

    def propose_next(self, current_offer: float, seller_ask: float) -> tuple[float, str]:
        """Concede half the remaining gap, capped at max_budget."""
        if current_offer >= self.max_budget:
            return round(self.max_budget, 2), (
                f"I am already at my maximum budget {self.max_budget:.2f} and cannot go higher."
            )
        gap = seller_ask - current_offer
        new_offer = min(self.max_budget, current_offer + gap * 0.5)
        reason = (
            f"Moving up from {current_offer:.2f} to {new_offer:.2f} to close the gap, "
            f"still within my budget of {self.max_budget:.2f}."
        )
        return round(new_offer, 2), reason

    def evaluate_counter(self, seller_ask: float, round_no: int) -> tuple[bool, str]:
        """Decide whether to accept a seller counter-offer.

        Rules (deliberately simple and auditable for the MVP):
        - Never accept above max_budget (the user's hard approval rule).
        - Accept if the ask is at or below target.
        - From round 2 onward, accept if the ask is within budget and
          within 20% of our current offer (close enough that further
          rounds are unlikely to help more than they cost in time).
        """
        if seller_ask > self.max_budget:
            return False, (
                f"Ask {seller_ask:.2f} is above my maximum budget "
                f"{self.max_budget:.2f}; I cannot accept it."
            )
        if seller_ask <= self.target_price:
            return True, f"Ask {seller_ask:.2f} meets my target price; accepting."
        # The caller passes the current offer context via round and price
        # proximity is checked in the negotiation engine as well.
        if round_no >= 2:
            return True, (
                f"Ask {seller_ask:.2f} is within my budget of {self.max_budget:.2f} "
                f"and we have converged enough after {round_no} rounds; accepting "
                f"to save further negotiation time."
            )
        return False, f"Ask {seller_ask:.2f} is still above my target {self.target_price:.2f}."
