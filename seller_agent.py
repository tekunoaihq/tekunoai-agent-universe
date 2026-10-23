"""Seller agent for TekunoAI Agent Universe.

The seller agent represents a seller / merchant. It never sells
below its floor price and concedes gradually from the list price.
Stdlib only.
"""
from __future__ import annotations

from dataclasses import dataclass

from marketplace import Listing


@dataclass
class SellerAgent:
    name: str
    listing: Listing

    @property
    def floor_price(self) -> float:
        return self.listing.floor_price

    @property
    def list_price(self) -> float:
        return self.listing.list_price

    def evaluate_offer(self, buyer_offer: float, current_ask: float) -> tuple[bool, str]:
        """Accept a buyer offer only if it respects the floor and is close to the ask."""
        if buyer_offer < self.floor_price:
            return False, (
                f"Offer {buyer_offer:.2f} is below my floor price "
                f"{self.floor_price:.2f}; I cannot sell at a loss."
            )
        if buyer_offer >= current_ask:
            return True, f"Offer {buyer_offer:.2f} meets my ask {current_ask:.2f}; accepting."
        gap_pct = (current_ask - buyer_offer) / current_ask if current_ask else 0
        if gap_pct <= 0.10:
            return True, (
                f"Offer {buyer_offer:.2f} is within 10% of my ask {current_ask:.2f} "
                f"and above my floor; accepting rather than risking the sale."
            )
        return False, (
            f"Offer {buyer_offer:.2f} is above my floor but still "
            f"{gap_pct * 100:.0f}% below my ask {current_ask:.2f}; countering."
        )

    def counter_offer(self, buyer_offer: float, current_ask: float) -> tuple[float, str]:
        """Concede 40% of the gap toward the buyer, never below the floor."""
        gap = current_ask - buyer_offer
        new_ask = max(self.floor_price, current_ask - gap * 0.4)
        if new_ask <= self.floor_price:
            reason = (
                f"Countering at {new_ask:.2f}, which is my floor price. "
                f"This is my final margin; I cannot go lower."
            )
        else:
            reason = (
                f"Countering at {new_ask:.2f}, down from {current_ask:.2f}. "
                f"I am conceding part of the gap while keeping margin above "
                f"my floor of {self.floor_price:.2f}."
            )
        return round(new_ask, 2), reason
