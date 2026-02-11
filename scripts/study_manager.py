#!/usr/bin/env python3
"""
Study Manager - Manages flashcard decks, quizzes, and spaced repetition data.

Uses SM-2 algorithm for spaced repetition scheduling.
Data stored in workspace/study-data/
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import sys

# Default data directory — configurable via STUDY_DATA_DIR env var.
# Auto-detects OpenClaw workspace if it exists, otherwise uses ~/.study-buddy/data/
def _default_data_dir() -> Path:
    """Pick the best default data directory for the current environment."""
    # 1. Explicit env var always wins
    env = os.environ.get("STUDY_DATA_DIR")
    if env:
        return Path(env)
    # 2. OpenClaw / ClawdBot workspace
    openclaw = Path.home() / ".openclaw" / "workspace" / "study-data"
    if openclaw.parent.exists():
        return openclaw
    # 3. Generic fallback
    return Path.home() / ".study-buddy" / "data"

DATA_DIR = _default_data_dir()


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_decks() -> dict:
    """Load all deck metadata."""
    ensure_data_dir()
    index_path = DATA_DIR / "decks.json"
    if index_path.exists():
        return json.loads(index_path.read_text())
    return {"decks": [], "stats": {"totalReviews": 0, "streak": 0, "lastStudy": None}}


def save_decks(data: dict):
    """Save deck metadata."""
    ensure_data_dir()
    index_path = DATA_DIR / "decks.json"
    index_path.write_text(json.dumps(data, indent=2, default=str))


def load_deck(deck_id: str) -> Optional[dict]:
    """Load a specific deck's cards."""
    deck_path = DATA_DIR / f"{deck_id}.json"
    if deck_path.exists():
        return json.loads(deck_path.read_text())
    return None


def save_deck(deck_id: str, deck_data: dict):
    """Save a deck's cards."""
    ensure_data_dir()
    deck_path = DATA_DIR / f"{deck_id}.json"
    deck_path.write_text(json.dumps(deck_data, indent=2, default=str))


def generate_deck_id(name: str) -> str:
    """Generate a unique deck ID from name."""
    slug = name.lower().replace(" ", "-")[:30]
    hash_suffix = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:6]
    return f"{slug}-{hash_suffix}"


def create_deck(name: str, source: str = "manual", cards: list = None) -> dict:
    """
    Create a new flashcard deck.
    
    Args:
        name: Deck name
        source: Where cards came from (manual, studium, pdf, etc.)
        cards: List of {"front": ..., "back": ...} dicts
    
    Returns:
        Deck metadata
    """
    deck_id = generate_deck_id(name)
    
    # Initialize cards with SM-2 defaults
    initialized_cards = []
    for i, card in enumerate(cards or []):
        initialized_cards.append({
            "id": f"{deck_id}-{i}",
            "front": card["front"],
            "back": card["back"],
            "interval": 1,  # days
            "ease": 2.5,    # ease factor
            "due": None,    # first review anytime
            "reps": 0,      # successful repetitions
            "created": datetime.now().isoformat()
        })
    
    # Save deck cards
    deck_data = {
        "id": deck_id,
        "name": name,
        "source": source,
        "cards": initialized_cards,
        "created": datetime.now().isoformat()
    }
    save_deck(deck_id, deck_data)
    
    # Update index
    data = load_decks()
    data["decks"].append({
        "id": deck_id,
        "name": name,
        "source": source,
        "cardCount": len(initialized_cards),
        "created": datetime.now().isoformat()
    })
    save_decks(data)
    
    return deck_data


def get_due_cards(deck_id: str = None) -> list:
    """Get all cards due for review."""
    now = datetime.now()
    due_cards = []
    
    if deck_id:
        deck = load_deck(deck_id)
        if deck:
            for card in deck["cards"]:
                if card["due"] is None or datetime.fromisoformat(card["due"]) <= now:
                    card["deck_id"] = deck_id
                    card["deck_name"] = deck["name"]
                    due_cards.append(card)
    else:
        data = load_decks()
        for deck_meta in data["decks"]:
            deck = load_deck(deck_meta["id"])
            if deck:
                for card in deck["cards"]:
                    if card["due"] is None or datetime.fromisoformat(card["due"]) <= now:
                        card["deck_id"] = deck_meta["id"]
                        card["deck_name"] = deck["name"]
                        due_cards.append(card)
    
    return due_cards


def update_card(deck_id: str, card_id: str, rating: int) -> dict:
    """
    Update card after review using SM-2 algorithm.
    
    Rating:
        0 = Again (complete failure)
        1 = Hard (correct with difficulty)
        2 = Good (correct with some hesitation)
        3 = Easy (perfect recall)
    
    Returns updated card data.
    """
    deck = load_deck(deck_id)
    if not deck:
        raise ValueError(f"Deck not found: {deck_id}")
    
    card = None
    card_idx = None
    for i, c in enumerate(deck["cards"]):
        if c["id"] == card_id:
            card = c
            card_idx = i
            break
    
    if not card:
        raise ValueError(f"Card not found: {card_id}")
    
    # SM-2 Algorithm
    interval = card.get("interval", 1)
    ease = card.get("ease", 2.5)
    reps = card.get("reps", 0)
    
    if rating == 0:  # Again
        # Reset to beginning
        interval = 1
        ease = max(1.3, ease - 0.2)
        reps = 0
    else:
        # Successful recall
        reps += 1
        
        if rating == 1:  # Hard
            interval = max(1, int(interval * 1.2))
            ease = max(1.3, ease - 0.15)
        elif rating == 2:  # Good
            if reps == 1:
                interval = 1
            elif reps == 2:
                interval = 6
            else:
                interval = int(interval * ease)
        elif rating == 3:  # Easy
            if reps == 1:
                interval = 4
            else:
                interval = int(interval * ease * 1.3)
            ease += 0.15
    
    # Update card
    card["interval"] = interval
    card["ease"] = round(ease, 2)
    card["reps"] = reps
    card["due"] = (datetime.now() + timedelta(days=interval)).isoformat()
    card["lastReview"] = datetime.now().isoformat()
    card["lastRating"] = rating
    
    deck["cards"][card_idx] = card
    save_deck(deck_id, deck)
    
    # Update stats
    data = load_decks()
    data["stats"]["totalReviews"] = data["stats"].get("totalReviews", 0) + 1
    today = datetime.now().date().isoformat()
    last_study = data["stats"].get("lastStudy")
    
    if last_study != today:
        if last_study:
            last_date = datetime.fromisoformat(last_study).date()
            if (datetime.now().date() - last_date).days == 1:
                data["stats"]["streak"] = data["stats"].get("streak", 0) + 1
            elif (datetime.now().date() - last_date).days > 1:
                data["stats"]["streak"] = 1
        else:
            data["stats"]["streak"] = 1
        data["stats"]["lastStudy"] = today
    
    # Track daily activity
    if "activity" not in data["stats"]:
        data["stats"]["activity"] = {}
    data["stats"]["activity"][today] = data["stats"]["activity"].get(today, 0) + 1
    
    save_decks(data)
    
    return card


def get_dashboard_data() -> dict:
    """Get data for the study dashboard."""
    data = load_decks()
    now = datetime.now()
    
    total_cards = 0
    due_today = 0
    mastered = 0  # Cards with interval > 21 days
    deck_summaries = []
    
    for deck_meta in data["decks"]:
        deck = load_deck(deck_meta["id"])
        if not deck:
            continue
        
        deck_due = 0
        deck_new = 0
        deck_mastered = 0
        
        for card in deck["cards"]:
            total_cards += 1
            
            if card["due"] is None:
                deck_new += 1
                due_today += 1
            elif datetime.fromisoformat(card["due"]) <= now:
                deck_due += 1
                due_today += 1
            
            if card.get("interval", 1) > 21:
                deck_mastered += 1
                mastered += 1
        
        deck_summaries.append({
            "id": deck_meta["id"],
            "name": deck_meta["name"],
            "source": deck_meta.get("source", "manual"),
            "cardCount": len(deck["cards"]),
            "due": deck_due,
            "new": deck_new,
            "mastered": deck_mastered
        })
    
    return {
        "totalCards": total_cards,
        "dueToday": due_today,
        "mastered": mastered,
        "streak": data["stats"].get("streak", 0),
        "decks": deck_summaries,
        "activity": data["stats"].get("activity", {})
    }


def delete_deck(deck_id: str) -> bool:
    """Delete a deck and its cards."""
    deck_path = DATA_DIR / f"{deck_id}.json"
    if deck_path.exists():
        deck_path.unlink()
    
    data = load_decks()
    data["decks"] = [d for d in data["decks"] if d["id"] != deck_id]
    save_decks(data)
    return True


def list_decks() -> list:
    """List all decks."""
    data = load_decks()
    return data["decks"]


def export_for_canvas(deck_id: str, template: str = "flashcards") -> str:
    """
    Export deck data as JavaScript for Canvas template.
    
    Args:
        deck_id: Deck to export
        template: "flashcards" or "quiz"
    
    Returns:
        JavaScript code to inject into template
    """
    deck = load_deck(deck_id)
    if not deck:
        raise ValueError(f"Deck not found: {deck_id}")
    
    if template == "flashcards":
        cards_js = json.dumps(deck["cards"])
        return f'const DECK_TITLE = {json.dumps(deck["name"])};\nconst CARDS = {cards_js};'
    
    elif template == "quiz":
        # Convert flashcards to quiz questions (basic true/false or recall)
        questions = []
        for card in deck["cards"]:
            questions.append({
                "question": card["front"],
                "options": [card["back"], "I don't know"],
                "correct": 0,
                "explanation": ""
            })
        return f'const QUIZ_TITLE = {json.dumps(deck["name"])};\nconst QUESTIONS = {json.dumps(questions)};'
    
    raise ValueError(f"Unknown template: {template}")


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Study Manager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # List decks
    subparsers.add_parser("list", help="List all decks")
    
    # Dashboard
    subparsers.add_parser("dashboard", help="Get dashboard data")
    
    # Due cards
    due_parser = subparsers.add_parser("due", help="Get due cards")
    due_parser.add_argument("--deck", help="Specific deck ID")
    
    # Create deck
    create_parser = subparsers.add_parser("create", help="Create a deck")
    create_parser.add_argument("name", help="Deck name")
    create_parser.add_argument("--source", default="manual", help="Source (manual, studium, pdf)")
    create_parser.add_argument("--cards", help="JSON file with cards")
    
    args = parser.parse_args()
    
    if args.command == "list":
        decks = list_decks()
        print(json.dumps(decks, indent=2))
    
    elif args.command == "dashboard":
        data = get_dashboard_data()
        print(json.dumps(data, indent=2))
    
    elif args.command == "due":
        cards = get_due_cards(args.deck)
        print(json.dumps(cards, indent=2))
    
    elif args.command == "create":
        cards = []
        if args.cards:
            cards = json.loads(Path(args.cards).read_text())
        deck = create_deck(args.name, args.source, cards)
        print(json.dumps(deck, indent=2))
