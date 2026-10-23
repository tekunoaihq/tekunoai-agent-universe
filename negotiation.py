"""Multi-round negotiation engine for TekunoAI Agent Universe.

Protocol in brief (full spec in docs/protocol.md):
1. Discovery: buyer finds a Listing.
2. Offer: buyer opens at target price, with a reason.
3. Counter: seller accepts, rejects, or counters above its floor, with a reason.
4. Convergence: both sides concede toward each other over multiple rounds,
   buyer capped at max_budget, seller floored at floor_price.
5. Outcome: DEAL at an agreed price, or WALK_AWAY when the buyer's budget
   and the seller's floor cannot meet within max_rounds.

Stdlib only. Deterministic, so demos and tests are reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from buyer_agent import BuyerAgent
from marketplace import Listing
from seller_agent import SellerAgent


@dataclass
class Message:
    round_no: int
    sender: str
    kind: str  # offer | counter | accept | reject | walk_away
    price: float | None
    reason: str

    def __str__(self) -> str:
        price = f"{self.price:.2f}" if self.price is not None else "-"
        return f"[Round {self.round_no}] {self.sender} ({self.kind} {price}): {self.reason}"


@dataclass
class NegotiationResult:
    deal_reached: bool
    final_price: float | None
    rounds_used: int
    listing: Listing
    transcript: list = field(default_factory=list)
    outcome_reason: str = ""

    def summary(self) -> str:
        if self.deal_reached:
            return (
                f"DEAL on '{self.listing.title}' at {self.listing.currency} "
                f"{self.final_price:.2f} after {self.rounds_used} round(s). "
                f"{self.outcome_reason}"
            )
        return (
            f"WALK_AWAY on '{self.listing.title}' after {self.rounds_used} round(s). "
            f"{self.outcome_reason}"
        )


class Negotiation:
    def __init__(
        self,
        buyer: BuyerAgent,
        seller: SellerAgent,
        listing: Listing,
        max_rounds: int = 5,
    ) -> None:
        if seller.listing.id != listing.id:
            raise ValueError("seller agent and listing do not match")
        self.buyer = buyer
        self.seller = seller
        self.listing = listing
        self.max_rounds = max_rounds
        self.transcript: list[Message] = []

    def _log(self, round_no: int, sender: str, kind: str, price, reason: str) -> Message:
        msg = Message(round_no=round_no, sender=sender, kind=kind, price=price, reason=reason)
        self.transcript.append(msg)
        return msg

    def run(self) -> NegotiationResult:
        seller_ask = self.listing.list_price
        buyer_offer, reason = self.buyer.initial_offer(self.listing.list_price)

        for round_no in range(1, self.max_rounds + 1):
            # --- Buyer offer ---
            self._log(round_no, self.buyer.name, "offer", buyer_offer, reason)

            # --- Seller evaluates buyer offer ---
            accepted, why = self.seller.evaluate_offer(buyer_offer, seller_ask)
            if accepted:
                self._log(round_no, self.seller.name, "accept", buyer_offer, why)
                return NegotiationResult(
                    deal_reached=True,
                    final_price=round(buyer_offer, 2),
                    rounds_used=round_no,
                    listing=self.listing,
                    transcript=list(self.transcript),
                    outcome_reason=f"Seller accepted the buyer's offer. {why}",
                )

            # --- Seller counters ---
            seller_ask, counter_reason = self.seller.counter_offer(buyer_offer, seller_ask)
            self._log(round_no, self.seller.name, "counter", seller_ask, counter_reason)

            # --- Buyer evaluates seller counter ---
            # Buyer only takes the round-2+ acceptance shortcut when the ask
            # is genuinely close to its own offer (within 20%).
            close_enough = seller_ask <= buyer_offer * 1.20
            if close_enough:
                buyer_accepts, why_buy = self.buyer.evaluate_counter(seller_ask, round_no)
            else:
                buyer_accepts, why_buy = False, (
                    f"Ask {seller_ask:.2f} is not yet close enough to my offer "
                    f"{buyer_offer:.2f}; continuing to negotiate."
                )
            if buyer_accepts:
                self._log(round_no, self.buyer.name, "accept", seller_ask, why_buy)
                return NegotiationResult(
                    deal_reached=True,
                    final_price=round(seller_ask, 2),
                    rounds_used=round_no,
                    listing=self.listing,
                    transcript=list(self.transcript),
                    outcome_reason=f"Buyer accepted the seller's counter. {why_buy}",
                )

            # No point continuing if neither side can move.
            if buyer_offer >= self.buyer.max_budget and seller_ask <= self.seller.floor_price:
                self._log(
                    round_no, self.buyer.name, "walk_away", None,
                    "Buyer is at max budget and seller is at floor price; no overlap exists.",
                )
                break

            if round_no == self.max_rounds:
                break

            # --- Buyer prepares next offer ---
            buyer_offer, reason = self.buyer.propose_next(buyer_offer, seller_ask)

        return NegotiationResult(
            deal_reached=False,
            final_price=None,
            rounds_used=len({m.round_no for m in self.transcript}) if self.transcript else self.max_rounds,
            listing=self.listing,
            transcript=list(self.transcript),
            outcome_reason=(
                f"No agreement within {self.max_rounds} rounds. Buyer budget was "
                f"{self.buyer.max_budget:.2f}, seller floor was {self.seller.floor_price:.2f}."
            ),
        )
