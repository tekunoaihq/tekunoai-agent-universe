# TekunoAI Agent Universe

**Status: MVP prototype in active development**

A two way AI agent universe where a user's buyer agent and a seller
agent discover, compare, negotiate and complete a purchase on the
user's behalf, within the user's budget and approval rules.

Built by **TekunoAI**
Founder: **Raghav Shah**

> This is an early prototype built to demonstrate the negotiation
> protocol and agent rules. It does not process real payments, and
> TekunoAI makes no claim here about customers, revenue or funding.

## The problem

Shopping today is one way and manual: a person searches, compares
tabs, guesses a fair price, and has no agent acting for them on the
other side of the transaction. Sellers, in turn, have no standard way
to negotiate with an automated buyer without giving away margin.

## Product concept

In the Agent Universe, both sides are represented by agents:

- A **buyer agent** acts for a human user. The user gives it a goal
  ("buy wireless headphones"), a target price, a hard max budget, and
  approval rules. The agent searches, shortlists, and negotiates.
- A **seller agent** acts for a merchant. It holds a list price and a
  private floor price it will never go below, and it negotiates to
  protect margin.
- The two agents exchange offers and counter offers, each with a
  human readable reason, until they reach a deal at a price that
  satisfies both sides, or walk away.

The user stays in control: the buyer agent can never agree to a price
above the user's max budget, and a future production version will ask
for explicit human approval before any payment above a set threshold.

This repository is the first working slice of that product: the
marketplace listing model and the multi round price negotiation
protocol, in plain Python with no external dependencies.

## Features

- Marketplace `Listing` model with list price, floor price, category,
  condition, currency and tags, with validation
- Buyer agent with target price and a hard max budget cap
- Seller agent with a private floor price it never crosses
- Multi round negotiation engine: offers, counter offers, reasons,
  acceptance and walk away outcomes
- Full negotiation transcript for every run, so a human can audit
  exactly why an agent offered or accepted a price
- Deterministic behaviour, so demos and tests are reproducible
- Demo script running two complete negotiations end to end
- Unit tests covering a successful deal and a walk away case
- Protocol specification in [`docs/protocol.md`](docs/protocol.md)

## Negotiation protocol (summary)

1. **Discovery**: buyer agent finds listings matching the request.
2. **Opening offer**: buyer opens at its target price, with a reason.
3. **Seller evaluation**: seller accepts, or counters above its floor.
4. **Convergence**: seller concedes 40% of the gap per round, buyer
   concedes 50% of the remaining gap per round, capped at its budget.
5. **Acceptance**: a price is agreed only if it is at or below the
   buyer's max budget AND at or above the seller's floor price.
6. **Walk away**: if prices cannot overlap within the round limit,
   no deal happens. Walking away is a valid, intended outcome.

Full step by step spec, message format and examples:
[`docs/protocol.md`](docs/protocol.md)

## Architecture

```mermaid
flowchart LR
    User["Human User<br/>budget + target + approval rules"] --> Buyer["Buyer Agent"]
    SellerHuman["Seller / Merchant<br/>list price + floor price"] --> Seller["Seller Agent"]
    Buyer -->|"search / shortlist"| Market["Marketplace<br/>Listing model"]
    Market --> Seller
    Buyer <->|"offers / counters<br/>with reasons"| Engine["Negotiation Engine<br/>multi-round protocol"]
    Engine <-> Seller
    Engine -->|"deal or walk-away<br/>+ full transcript"| Result["Negotiation Result"]
    Result --> User
```

## Tech stack

- Python 3.10+ (standard library only, no external dependencies)
- `dataclasses` for Listing, agents, messages and results
- `unittest` for tests
- Planned for later versions: LLM reasoning for offer explanations,
  a web API, multi-seller comparison, and a payment / approval step.
  None of those are in this MVP yet.

## How to run

```bash
# Clone (once published) or open this folder, then:
cd tekunoai-agent-universe

# Run the demo: two negotiations, with full transcripts
python3 demo.py

# Run the tests
python3 -m unittest discover -s tests -v
```

Expected demo outcome:

- Negotiation 1, headphones listed at 120 (floor 80), buyer budget
  100, target 70: **DEAL** at a price within budget and above floor.
- Negotiation 2, premium watch listed at 500 (floor 450), buyer
  budget 300: **WALK_AWAY**, because budget and floor never overlap.

## Project structure

```
tekunoai-agent-universe/
  README.md
  LICENSE
  marketplace.py      Listing model
  buyer_agent.py      Buyer agent (budget + target rules)
  seller_agent.py     Seller agent (floor price rules)
  negotiation.py      Multi-round negotiation engine + transcript
  demo.py             Two end-to-end example negotiations
  docs/
    protocol.md       Negotiation protocol specification
  tests/
    test_negotiation.py  Deal, walk-away and validation tests
```

## Roadmap

- [x] Listing model and price negotiation protocol (this MVP)
- [x] Buyer and seller agents with hard budget / floor rules
- [x] Transcript, demo and tests
- [ ] Compare multiple seller agents in parallel, pick the best deal
- [ ] Negotiate on shipping, delivery time and returns, not just price
- [ ] LLM generated negotiation reasons on top of the auditable rules
- [ ] Human approval step before a purchase is confirmed
- [ ] Web API and a simple UI for creating a buying request
- [ ] Agent identity, reputation and seller verification
- [ ] Payment and escrow integration (design only, no real payments in MVP)

## Part of TekunoAI

TekunoAI is building AI native digital products, including:

- An AI SDLC management system
- AI powered event management
- The AI Agent Universe (this repository)

## License

MIT, see [LICENSE](LICENSE).
