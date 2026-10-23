"""Demo: run two end-to-end negotiations and print the transcripts.

Run:  python3 demo.py
"""
from __future__ import annotations

from buyer_agent import BuyerAgent
from marketplace import Listing
from negotiation import Negotiation
from seller_agent import SellerAgent


def run_one(title: str, listing: Listing, buyer: BuyerAgent) -> None:
    print("=" * 72)
    print(title)
    print(listing.summary())
    print(f"Buyer: {buyer.name} | target {buyer.target_price:.2f} | max budget {buyer.max_budget:.2f}")
    print("-" * 72)
    seller = SellerAgent(name=f"SellerAgent({listing.seller_id})", listing=listing)
    result = Negotiation(buyer=buyer, seller=seller, listing=listing, max_rounds=5).run()
    for msg in result.transcript:
        print(msg)
    print("-" * 72)
    print("RESULT:", result.summary())
    print()


def main() -> None:
    # Negotiation 1: prices overlap -> expect a DEAL
    headphones = Listing(
        id="listing-headphones-001",
        title="Wireless Noise Cancelling Headphones",
        seller_id="seller-audio-store",
        list_price=120.00,
        floor_price=80.00,
        category="electronics",
        description="Over-ear wireless headphones, 30h battery.",
        tags=["audio", "headphones", "wireless"],
    )
    buyer_1 = BuyerAgent(name="BuyerAgent(Raghav)", max_budget=100.00, target_price=70.00)
    run_one("Negotiation 1: Headphones (budget and floor overlap)", headphones, buyer_1)

    # Negotiation 2: buyer budget is below seller floor -> expect WALK_AWAY
    watch = Listing(
        id="listing-watch-001",
        title="Premium Automatic Watch",
        seller_id="seller-watch-store",
        list_price=500.00,
        floor_price=450.00,
        category="fashion",
        description="Automatic movement watch, sapphire glass.",
        tags=["watch", "premium"],
    )
    buyer_2 = BuyerAgent(name="BuyerAgent(Raghav)", max_budget=300.00, target_price=250.00)
    run_one("Negotiation 2: Premium Watch (budget below seller floor)", watch, buyer_2)

    print("Demo complete: 1 deal + 1 walk-away, both within the buyer's approval rules.")


if __name__ == "__main__":
    main()
