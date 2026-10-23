# TekunoAI Agent Universe: Negotiation Protocol

Version: 0.1 (MVP prototype)
Status: MVP prototype in active development

This document describes how a buyer agent and a seller agent negotiate
a purchase in the Agent Universe. The reference implementation is in
`negotiation.py`, `buyer_agent.py`, `seller_agent.py` and
`marketplace.py` in this repository.

## Actors

- **User**: a human who sets a max budget, a target price, and approval
  rules. The user is the final authority.
- **Buyer Agent**: acts for the user. Discovers listings, compares
  options, and negotiates. It must never agree to a price above the
  user's max budget.
- **Seller Agent**: acts for a seller. It lists an item at a list price
  and must never sell below its floor price.
- **Listing**: a marketplace item with an id, title, seller, category,
  list price, floor price, currency, condition and description.

## Hard rules (approval rules)

1. Buyer agent: `agreed_price <= user max_budget`, always.
2. Seller agent: `agreed_price >= seller floor_price`, always.
3. Every offer and counter must carry a human readable reason.
4. If the rules cannot both be satisfied, the outcome is a walk-away,
   not a forced deal.
5. In a future production version, a deal above a user set threshold
   will require explicit human approval before payment. The MVP does
   not process real payments.

## Protocol steps

### Step 1: Discovery
The buyer agent searches marketplace listings matching the user's
request (category, tags, condition, price range) and shortlists
candidates at or near the user's budget.

### Step 2: Opening offer
The buyer agent opens at the user's target price:

```
Buyer -> Seller: OFFER(price=target_price, reason="Opening at target...")
```

### Step 3: Seller evaluation
The seller agent checks the offer against its floor:

- If `offer < floor_price`: reject the offer price and counter.
- If `offer >= current ask`: accept.
- If `offer` is within 10% of the current ask and above the floor:
  accept, rather than risk losing the sale.
- Otherwise: counter.

### Step 4: Counter offer
The seller concedes 40% of the gap between its current ask and the
buyer's offer, never going below its floor:

```
Seller -> Buyer: COUNTER(price=new_ask, reason="Conceding part of the gap...")
new_ask = max(floor_price, current_ask - 0.40 * (current_ask - buyer_offer))
```

### Step 5: Buyer evaluation
The buyer agent checks the counter against the user's rules:

- If `ask > max_budget`: refuse, it can never be accepted.
- If `ask <= target_price`: accept.
- From round 2 onward, if the ask is within budget and within 20% of
  the buyer's current offer: accept, because prices have converged.
- Otherwise: prepare a new offer.

### Step 6: Buyer concession
If negotiation continues, the buyer concedes half the remaining gap,
capped at its max budget:

```
Buyer -> Seller: OFFER(price=new_offer, reason="Moving up to close the gap...")
new_offer = min(max_budget, current_offer + 0.50 * (seller_ask - current_offer))
```

Steps 3 to 6 repeat for up to `max_rounds` (default 5).

### Step 7: Outcome

- **DEAL**: one side accepts. The agreed price, the listing, and the
  full transcript are recorded in a `NegotiationResult`.
- **WALK_AWAY**: rounds are exhausted, or the buyer is at its max
  budget while the seller is at its floor and the prices still do not
  overlap. No purchase happens and no payment is attempted.

## Message format

Each step is a `Message` in the transcript:

| Field | Meaning |
|---|---|
| `round_no` | 1-based negotiation round |
| `sender` | Agent name |
| `kind` | `offer`, `counter`, `accept`, `reject`, or `walk_away` |
| `price` | Price for this message, or null for walk-away |
| `reason` | Human readable justification for the move |

## Example outcomes

- Headphones listed at 120, floor 80, buyer target 70, budget 100:
  the agents converge and reach a deal within budget and above floor.
- Premium watch listed at 500, floor 450, buyer budget 300:
  budget and floor never overlap, so the buyer agent walks away.

Both examples run in `demo.py`.

## Future protocol work

- Multi-item and bundle negotiation
- Comparing multiple seller agents in parallel and picking the best deal
- Shipping, tax, delivery time and returns as negotiation terms, not
  just price
- Reputation and identity verification for agents
- Human approval step and payment escrow integration
- LLM based reasoning for reasons, on top of these auditable rules
