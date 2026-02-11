# Study Buddy — Agent Instructions

This skill helps users create and study flashcards and quizzes with spaced repetition.

## Quick Commands

| User Says | Do This |
|-----------|---------|
| "Make flashcards for..." | Generate cards, create deck, present in Canvas |
| "Quiz me on..." | Generate quiz questions, present interactive quiz |
| "What's due for review?" | Check due cards, start study session |
| "Show my study dashboard" | Display progress dashboard |

## Workflow

### Creating Flashcards

1. Parse the content (pasted text, Studium content, etc.)
2. Generate front/back pairs for key concepts
3. Call `create_deck()` from `scripts/study_manager.py`
4. Present via Canvas with `assets/flashcards.html`

### Running a Quiz

1. Generate questions with options and correct answers
2. Inject into `assets/quiz.html` template
3. Present via Canvas
4. Log results when complete

### Spaced Repetition

Cards track: `interval`, `ease`, `due`, `reps`

After each review, user rates:
- **Again (0)** — Forgot, reset
- **Hard (1)** — Difficult, short interval
- **Good (2)** — Normal, standard interval  
- **Easy (3)** — Perfect, long interval

Use `update_card(deck_id, card_id, rating)` to apply SM-2 algorithm.

## Key Files

- `scripts/study_manager.py` — Deck/card CRUD, SM-2 logic
- `scripts/studium_quiz.py` — Canvas LMS integration
- `assets/flashcards.html` — Flashcard UI template
- `assets/quiz.html` — Quiz UI template
- `assets/dashboard.html` — Dashboard UI template

## Example: Create Deck

```python
from scripts.study_manager import create_deck

cards = [
    {"front": "What is HTTP?", "back": "HyperText Transfer Protocol"},
    {"front": "What is DNS?", "back": "Domain Name System"},
]

deck = create_deck("Networking Basics", source="manual", cards=cards)
```

## Example: Present Flashcards

```python
from scripts.study_manager import load_deck
import json

deck = load_deck(deck_id)
js_data = f'''
const DECK_TITLE = {json.dumps(deck["name"])};
const CARDS = {json.dumps(deck["cards"])};
'''

# Read template, inject data, present via canvas tool
```

## Data Location

`~/.openclaw/workspace/study-data/`

See SKILL.md for detailed instructions.
