---
name: study-buddy
description: Generate interactive quizzes, flashcards, and study materials from any content. Uses spaced repetition (Anki-style SM-2) for effective learning. Produces self-contained HTML widgets that render inline. Integrates with Studium (Canvas LMS) and supports PDFs. Use this skill whenever students want to study, review, create flashcards, take quizzes, learn from course materials, memorize vocabulary, or prepare for exams — even if they don't explicitly say "flashcard" or "quiz".
---

# Study Buddy

Transform any learning material into interactive study sessions with spaced repetition.

## Quick Start

```
User: "Quiz me on my latest lecture"
User: "Make flashcards from my NLP course"
User: "Create a quiz from this week's readings"
User: "Make flashcards from these notes: [content]"
User: "What should I study today?"
```

## First-Time Setup: Connecting to Studium

The primary content source is Studium (Uppsala University's Canvas LMS). On first use, walk the user through connecting their account. This only needs to happen once.

### Onboarding Flow

When the user asks to study from their courses and no `.env.studium` file exists (or `STUDIUM_API_KEY` is not set), present the interactive setup page.

**Step 1 — Show the setup widget:**

Present `assets/setup.html` as an inline widget. It contains step-by-step instructions for generating a Canvas API token and a password field where the user can paste it securely.

```python
from pathlib import Path

skill_dir = Path("<skill-directory>")
setup_html = (skill_dir / "assets" / "setup.html").read_text()
Path("<outputs-folder>/studium-setup.html").write_text(setup_html)
```

Then link it: `[Connect to Studium](computer://<outputs-folder>/studium-setup.html)`

Tell the user: "I've opened the setup page — follow the steps there to connect your Studium account. Once you paste your token, let me know and I'll save it."

**Step 2 — Save the token:**

When the user provides the token (either through the widget or pasted into chat), save it:

```python
from pathlib import Path

skill_dir = Path("<skill-directory>")
env_content = f'''export STUDIUM_API_KEY="{user_token}"
export STUDIUM_BASE_URL="https://uppsala.instructure.com"
'''
(skill_dir / ".env.studium").write_text(env_content)
```

**Step 3 — Verify the connection:**

Test that it works by fetching their courses:

```bash
source <skill-directory>/.env.studium
python3 <skill-directory>/scripts/studium_quiz.py courses
```

If courses come back, tell the user which courses were found and ask which one they'd like to study from. If it fails, help troubleshoot (wrong token, expired, network issue).

### Returning Users

On subsequent uses, load the saved credentials:

```bash
source <skill-directory>/.env.studium
```

If the file exists and the token works, skip the onboarding and go straight to fetching content.

## How It Works — Three Steps

Every workflow follows the same pattern:

1. **Get content** — from Studium courses, user-pasted text, or a PDF
2. **Generate questions** — flashcards or quiz questions from the content
3. **Present interactively** — write a self-contained HTML file and show it inline

## Fetching Content from Studium

Once connected, pull course content like this:

```bash
source <skill-directory>/.env.studium

# List the user's courses
python3 <skill-directory>/scripts/studium_quiz.py courses

# Get the latest lecture/page content from a course
python3 <skill-directory>/scripts/studium_quiz.py latest --course <course_id>

# Generate a quiz prompt from the latest content
python3 <skill-directory>/scripts/studium_quiz.py prompt --course <course_id> --type quiz

# Or generate a flashcard prompt
python3 <skill-directory>/scripts/studium_quiz.py prompt --course <course_id> --type flashcards
```

The `prompt` command returns a structured prompt with the content embedded. Use it to generate questions, then inject them into the HTML templates.

### Full "Quiz me on my latest lecture" Workflow

1. Load credentials: `source <skill-directory>/.env.studium`
2. Fetch courses: `python3 scripts/studium_quiz.py courses`
3. If the user hasn't specified a course, show the list and ask which one
4. Get latest content: `python3 scripts/studium_quiz.py latest --course <id>`
5. Generate quiz questions from the returned text (the LLM does this part)
6. Save deck with `study_manager.create_deck()`
7. Inject into the quiz HTML template and present inline

## Presenting Content (Platform-Adaptive)

The skill produces self-contained HTML files by injecting data into templates. The data injection step is the same everywhere — only the final "show it to the user" step differs per platform. Detect which environment you're in and use the matching method.

### Step 1 (all platforms): Build the HTML

```python
import json
from pathlib import Path

# 1. Read the template
skill_dir = Path("<skill-directory>")
template = (skill_dir / "assets" / "quiz.html").read_text()

# 2. Build the JS data block
js_data = f'''
const QUIZ_TITLE = {json.dumps(title)};
const QUESTIONS = {json.dumps(questions)};
'''

# 3. Inject into template (replaces the placeholder comment)
html = template.replace("/*QUESTIONS_DATA*/", js_data)
```

### Step 2: Present it (pick the right method for the environment)

#### OpenClaw / ClawdBot (Canvas tool available)

If you have access to the `canvas` tool, use it directly. This is the primary path for OpenClaw and ClawdBot — it presents the HTML inline in the chat.

```python
# Option A: Write to temp file and present (best for larger content)
Path("/tmp/study-session.html").write_text(html)
canvas(action="present", url="file:///tmp/study-session.html")

# Option B: Data URL (works for smaller content)
import urllib.parse
canvas(action="present", url=f"data:text/html;charset=utf-8,{urllib.parse.quote(html)}")
```

The Canvas receives postMessage events for interactive feedback:
- `cardUpdate` — card was reviewed (save to study-data)
- `quizComplete` — quiz finished (log results)
- `sessionComplete` — flashcard session done

#### Claude Desktop / Cowork (file + computer:// link)

Write the HTML file to the **outputs folder** and link it with a `computer://` URL so it renders as an inline widget:

```python
output_path = Path("<outputs-folder>/quiz.html")
output_path.write_text(html)
# Then show: [Take the quiz](computer://<outputs-folder>/quiz.html)
```

Use descriptive filenames like `nlp-lecture-3-quiz.html` or `swedish-vocab-flashcards.html`.

#### Codex CLI / Terminal (file + browser)

Write the file and tell the user to open it in their browser:

```python
output_path = Path("/tmp/study-session.html")
output_path.write_text(html)
# Tell user: "Quiz saved to /tmp/study-session.html — open it in your browser."
```

## Core Workflows

### 1. Creating Flashcards

From any content, generate card pairs:

```python
cards = [
    {"front": "What does HTTP stand for?", "back": "HyperText Transfer Protocol"},
    {"front": "What layer is TCP?", "back": "Transport layer (Layer 4)"},
]
```

Save the deck:

```python
from scripts.study_manager import create_deck
deck = create_deck("Networking Basics", source="manual", cards=cards)
```

### 2. Presenting Flashcards

Inject data into `assets/flashcards.html`:

```python
import json
from pathlib import Path

deck = load_deck(deck_id)
js_data = f'''
const DECK_TITLE = {json.dumps(deck["name"])};
const CARDS = {json.dumps(deck["cards"])};
'''

template = Path("<skill-directory>/assets/flashcards.html").read_text()
html = template.replace("/*CARDS_DATA*/", js_data)
```

Then present using the platform-appropriate method (see "Presenting Content" section above):
- **OpenClaw/ClawdBot**: `canvas(action="present", url="file:///tmp/flashcards.html")`
- **Claude Desktop**: Write to outputs folder, link with `computer://`
- **Codex CLI**: Write to file, tell user to open in browser

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

Inject into `assets/quiz.html` using the `/*QUESTIONS_DATA*/` placeholder, same pattern as flashcards.

### 4. Spaced Repetition (SM-2)

After each card review, user rates recall:

- **Again (0)**: Complete failure — reset, review soon
- **Hard (1)**: Correct with difficulty — short interval
- **Good (2)**: Correct with hesitation — normal interval
- **Easy (3)**: Perfect recall — longer interval

```python
from scripts.study_manager import update_card
update_card(deck_id, card_id, rating=2)  # Good
```

### 5. Dashboard

Show study progress:

```python
from scripts.study_manager import get_dashboard_data
data = get_dashboard_data()
```

Inject into `assets/dashboard.html` using the `/*STUDY_DATA*/` placeholder.

## Data Storage

The study manager stores data in a configurable location. Set the `STUDY_DATA_DIR` environment variable, or it defaults to `~/.study-buddy/data/`.

```python
# Override data location if needed
import scripts.study_manager as sm
sm.DATA_DIR = Path("/custom/path/study-data")
```

Files stored:

- `decks.json` — Deck index and global stats
- `{deck-id}.json` — Individual deck cards with spaced repetition data

## Question Generation Guidelines

When generating questions from content:

1. **Cover key concepts** — focus on main ideas, not trivia
2. **Vary difficulty** — mix recall, comprehension, and application questions
3. **Clear distractors** — wrong options should be plausible but clearly wrong
4. **Concise wording** — avoid unnecessarily complex phrasing
5. **One concept per card** — atomic knowledge units

See `references/question-patterns.md` for Bloom's taxonomy patterns and templates.

**Good flashcard:**
- Front: "What does HTTP stand for?"
- Back: "HyperText Transfer Protocol"

**Bad flashcard:**
- Front: "Explain everything about HTTP including its history, methods, and status codes"
- Back: [wall of text]

## Examples

**"Create flashcards for Swedish vocabulary"**
1. Generate Swedish-English card pairs
2. Create deck with `create_deck("Swedish Vocab", cards=...)`
3. Write flashcards HTML and present inline

**"Quiz me on Chapter 5"**
1. User provides or pastes chapter content
2. Generate 10-15 multiple choice questions
3. Write quiz HTML and present inline
4. Report score when quiz is complete

**"What's due for review?"**
1. Call `get_due_cards()`
2. If cards due: build flashcard session, present inline
3. If none: "All caught up! Next review: [date]"

**"Show my study stats"**
1. Call `get_dashboard_data()`
2. Write dashboard HTML and present inline
