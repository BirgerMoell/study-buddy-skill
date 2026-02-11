---
name: study-buddy
description: Generate interactive quizzes, flashcards, and study materials from any content. Uses spaced repetition (Anki-style SM-2) for effective learning. Displays via Canvas for inline interactive experience. Integrates with Studium (Canvas LMS) and supports PDFs. Use when students want to study, review, create flashcards, take quizzes, or learn from course materials.
---

# Study Buddy

Transform any learning material into interactive study sessions with spaced repetition.

## Quick Start

### From Studium (Primary Flow)
```
User: "Quiz me on my latest lecture"
User: "Make flashcards from my NLP course"
User: "Create a quiz from this week's readings"
→ Fetch from Studium → Generate questions → Present in Canvas
```

### From Pasted Content
```
User: "Make flashcards from these notes: [content]"
→ Generate cards, save deck, present in Canvas
```

### Review Due Cards
```
User: "What should I study today?"
→ Show due cards from spaced repetition queue
```

## Studium Integration (Primary)

### Fetch Latest Lecture → Generate Quiz

```python
# 1. Get content from Studium
import os
os.environ["STUDIUM_API_KEY"] = "..."  # From .env.studium

from scripts.studium_quiz import find_latest_lecture_content, generate_quiz_prompts

# Find recent content
content = find_latest_lecture_content(course_id=None)  # Auto-picks recent course
# Or specify: find_latest_lecture_content(course_id=12345)

# 2. Generate prompt for quiz/flashcards
prompt = generate_quiz_prompts(content["latest"]["content"], content["latest"]["title"])
# Or: generate_flashcard_prompts(...)

# 3. Use LLM to generate questions from prompt
# (The prompt is designed for the agent to process)

# 4. Save and present
```

### Full "Quiz me on my latest lecture" Workflow

1. **Load Studium credentials**: `source .env.studium`
2. **Fetch courses**: `python3 scripts/studium_quiz.py courses`
3. **Get latest content**: `python3 scripts/studium_quiz.py latest --course <id>`
4. **Generate questions** from the content (LLM generates from returned text)
5. **Save deck**: Use `study_manager.create_deck()`
6. **Present via Canvas**: Inject into quiz.html or flashcards.html

## Core Workflows

### 1. Creating Flashcards

From pasted content:
```python
# Generate card pairs from content
cards = [
    {"front": "Question/term", "back": "Answer/definition"},
    ...
]

# Save deck
from scripts.study_manager import create_deck
deck = create_deck("Deck Name", source="manual", cards=cards)
```

From Studium:
```bash
# Get course materials
source .env.studium
python3 skills/studium/scripts/studium.py assignments <course_id>

# Create deck from assignment/readings
```

From PDF:
```bash
# Extract text first, then generate cards from content
```

### 2. Presenting Flashcards

Inject data into `assets/flashcards.html`:

```python
# Generate JavaScript data
deck = load_deck(deck_id)
js_data = f'''
const DECK_TITLE = "{deck['name']}";
const CARDS = {json.dumps(deck['cards'])};
'''

# Read template, inject data, present
template = Path("assets/flashcards.html").read_text()
html = template.replace("/*CARDS_DATA*/", js_data)

# Present via Canvas
```

Then use canvas tool:
```
canvas action=present url="data:text/html,..." 
```

Or write to temp file and present.

### 3. Generating Quizzes

Create varied question types from content:

**Multiple Choice:**
```json
{
  "question": "What is the capital of Sweden?",
  "options": ["Oslo", "Stockholm", "Copenhagen", "Helsinki"],
  "correct": 1,
  "explanation": "Stockholm has been Sweden's capital since 1436."
}
```

**True/False:**
```json
{
  "question": "DNA stands for Deoxyribonucleic Acid.",
  "options": ["True", "False"],
  "correct": 0
}
```

Inject into `assets/quiz.html`:
```python
js_data = f'''
const QUIZ_TITLE = "Quiz Title";
const QUESTIONS = {json.dumps(questions)};
'''
```

### 4. Spaced Repetition (SM-2)

After each card review, user rates recall:
- **Again (0)**: Complete failure → reset, review soon
- **Hard (1)**: Correct with difficulty → short interval
- **Good (2)**: Correct with hesitation → normal interval
- **Easy (3)**: Perfect recall → longer interval

The algorithm adjusts:
- `interval`: Days until next review
- `ease`: Multiplier for future intervals (starts at 2.5)

```python
from scripts.study_manager import update_card
update_card(deck_id, card_id, rating=2)  # Good
```

### 5. Dashboard

Show study progress:
```python
from scripts.study_manager import get_dashboard_data
data = get_dashboard_data()
# Returns: totalCards, dueToday, mastered, streak, decks, activity
```

Present via `assets/dashboard.html`.

## Data Storage

All study data stored in `workspace/study-data/`:
- `decks.json` - Deck index and global stats
- `{deck-id}.json` - Individual deck cards with SR data

## Studium Integration

Pull materials from Uppsala University's Canvas LMS:

```bash
source .env.studium

# Get course list
python3 skills/studium/scripts/studium.py courses

# Get assignments
python3 skills/studium/scripts/studium.py assignments <course_id>

# Get specific content
python3 skills/studium/scripts/studium.py download <course_id> --type pages
```

Then generate cards/quizzes from the content.

## Question Generation Guidelines

When generating questions from content:

1. **Cover key concepts** - Focus on main ideas, not trivia
2. **Vary difficulty** - Mix recall, comprehension, application
3. **Clear distractors** - Wrong options should be plausible but clearly wrong
4. **Concise wording** - Avoid unnecessarily complex phrasing
5. **One concept per card** - Atomic knowledge units

**Good flashcard:**
- Front: "What does HTTP stand for?"
- Back: "HyperText Transfer Protocol"

**Bad flashcard:**
- Front: "Explain everything about HTTP including its history, methods, and status codes"
- Back: [wall of text]

## Canvas Presentation

Use the canvas tool to display interactive UIs:

```python
# Option 1: Data URL (for small content)
html_content = "..."  # Full HTML with injected data
canvas(action="present", url=f"data:text/html;charset=utf-8,{urllib.parse.quote(html_content)}")

# Option 2: File (for larger content)
Path("/tmp/study-session.html").write_text(html_content)
canvas(action="present", url="file:///tmp/study-session.html")
```

The Canvas receives postMessage events for:
- `cardUpdate` - Card was reviewed (save to study-data)
- `quizComplete` - Quiz finished (log results)
- `sessionComplete` - Flashcard session done

## Examples

**"Create flashcards for Swedish vocabulary"**
1. Generate Swedish-English pairs
2. Create deck with `create_deck("Swedish Vocab", cards=...)`
3. Present flashcards via Canvas

**"Quiz me on Chapter 5"**
1. User provides/pastes chapter content
2. Generate 10-15 multiple choice questions
3. Present quiz via Canvas
4. Report score when complete

**"What's due for review?"**
1. Call `get_due_cards()`
2. If cards due: present flashcard session
3. If none: "All caught up! Next review: [date]"

**"Show my study stats"**
1. Call `get_dashboard_data()`
2. Present dashboard via Canvas
