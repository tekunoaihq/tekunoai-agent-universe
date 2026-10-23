"""Tests for TekunoAI Agent Universe negotiation engine.

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from buyer_agent import BuyerAgent
from marketplace import Listing
from negotiation import Negotiation
from seller_agent import SellerAgent


def make_listing(list_price=120.0, floor_price=80.0):
    return Listing(
        id="listing-test-001",
        title="Test Headphones",
        seller_id="seller-test",
        list_price=list_price,
        floor_price=floor_price,
        category="electronics",
    )


class TestSuccessfulDeal(unittest.TestCase):
    def test_deal_within_budget_and_above_floor(self):
        listing = make_listing()
        buyer = BuyerAgent(name="BuyerAgent(Test)", max_budget=100.0, target_price=70.0)
        seller = SellerAgent(name="SellerAgent(Test)", listing=listing)
        result = Negotiation(buyer=buyer, seller=seller, listing=listing).run()

        self.assertTrue(result.deal_reached)
        self.assertIsNotNone(result.final_price)
        # User approval rule: never above max budget.
        self.assertLessEqual(result.final_price, buyer.max_budget)
        # Seller rule: never below floor.
        self.assertGreaterEqual(result.final_price, listing.floor_price)
        self.assertGreater(len(result.transcript), 0)

    def test_transcript_has_offers_and_reasons(self):
        listing = make_listing()
        buyer = BuyerAgent(name="BuyerAgent(Test)", max_budget=100.0, target_price=70.0)
        seller = SellerAgent(name="SellerAgent(Test)", listing=listing)
        result = Negotiation(buyer=buyer, seller=seller, listing=listing).run()
        kinds = [m.kind for m in result.transcript]
        self.assertIn("offer", kinds)
        self.assertTrue(all(m.reason for m in result.transcript))


class TestWalkAway(unittest.TestCase):
    def test_walk_away_when_budget_below_floor(self):
        listing = make_listing(list_price=500.0, floor_price=450.0)
        buyer = BuyerAgent(name="BuyerAgent(Test)", max_budget=300.0, target_price=250.0)
        seller = SellerAgent(name="SellerAgent(Test)", listing=listing)
        result = Negotiation(buyer=buyer, seller=seller, listing=listing).run()

        self.assertFalse(result.deal_reached)
        self.assertIsNone(result.final_price)

    def test_buyer_never_exceeds_budget_in_transcript(self):
        listing = make_listing(list_price=500.0, floor_price=450.0)
        buyer = BuyerAgent(name="BuyerAgent(Test)", max_budget=300.0, target_price=250.0)
        seller = SellerAgent(name="SellerAgent(Test)", listing=listing)
        result = Negotiation(buyer=buyer, seller=seller, listing=listing).run()
        for msg in result.transcript:
            if msg.kind == "offer" and msg.price is not None:
                self.assertLessEqual(msg.price, buyer.max_budget)


class TestListingValidation(unittest.TestCase):
    def test_floor_cannot_exceed_list(self):
        with self.assertRaises(ValueError):
            make_listing(list_price=50.0, floor_price=80.0)


if __name__ == "__main__":
    unittest.main()
