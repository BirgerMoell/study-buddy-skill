# Study Buddy 🧠

**Transform any learning material into interactive flashcards and quizzes with spaced repetition.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://birgermoell.github.io/study-buddy-skill/)

---

## Features

- 🎴 **Smart Flashcards** — Auto-generate from any text
- 📝 **Interactive Quizzes** — Multiple choice with instant feedback
- 🔄 **Spaced Repetition** — SM-2 algorithm for optimal review timing
- 📊 **Progress Dashboard** — Track streaks, mastery, and activity
- 🎓 **Canvas LMS Integration** — Pull materials from Studium/Canvas
- 📄 **PDF Support** — Extract and study from documents

## Installation

### Claude Desktop (Cowork Mode)

**Step 1:** Clone the repo to a folder on your machine:

```bash
git clone https://github.com/birgermoell/study-buddy-skill.git
```

**Step 2:** Open Claude Desktop and start a Cowork session. Select the `study-buddy-skill` folder as your workspace.

**Step 3:** That's it — Claude reads `SKILL.md` automatically. Just say:

```
"Make flashcards for photosynthesis, mitosis, and osmosis"
```

Claude will generate the content, build an interactive HTML widget, and display it inline in the conversation. Quizzes and flashcards are fully interactive — click answers, flip cards, rate your recall.

**Optional — Connect to Studium (Canvas LMS):**

If you're at Uppsala University and want to pull course content automatically, say:

```
"Connect to Studium" or "Quiz me on my latest lecture"
```

Claude will walk you through generating a Canvas API token and saving it. After that, it can fetch your lectures and generate quizzes from them.

### OpenClaw / ClawdBot

**Step 1:** Clone into the skills directory:

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/birgermoell/study-buddy-skill.git study-buddy
```

**Step 2:** Done! OpenClaw auto-discovers skills from the workspace. Just ask:

```
"Create flashcards for..."
"Quiz me on..."
```

The skill uses the `canvas` tool to present interactive HTML widgets inline in the chat. Study data is stored in `~/.openclaw/workspace/study-data/`.

### Codex CLI

**Step 1:** Clone the repo:

```bash
git clone https://github.com/birgermoell/study-buddy-skill.git
```

**Step 2:** Reference the skill in your project's `AGENTS.md`:

```markdown
## External Skills
- [Study Buddy](./study-buddy-skill/AGENTS.md) - Flashcards & Quizzes
```

**Step 3:** The agent reads `AGENTS.md` and `SKILL.md` for instructions. When it generates quizzes or flashcards, it writes HTML files and tells you to open them in your browser.

## Usage Examples

```
"Make flashcards for these terms: photosynthesis, mitosis, osmosis"

"Quiz me on Chapter 5"

"What cards are due for review?"

"Show my study dashboard"

"Create a deck from my latest Studium lecture"
```

## How It Works

### The Flow

1. **You ask** — "Quiz me on transformers" or "Make flashcards for Swedish vocab"
2. **Content is gathered** — from your text, a PDF, or Studium courses
3. **Questions are generated** — the AI creates flashcards or quiz questions
4. **An interactive widget appears** — a self-contained HTML file rendered inline

### Platform-Adaptive Presentation

The same HTML templates work everywhere — only the delivery method differs:

| Platform | How it's shown |
|---|---|
| **Claude Desktop** | HTML file written to workspace, rendered inline via `computer://` link |
| **OpenClaw / ClawdBot** | HTML presented via `canvas` tool inline in chat |
| **Codex CLI** | HTML file saved, user opens in browser |

### Spaced Repetition (SM-2)

After each card, rate your recall:

| Rating | Meaning | Effect |
|--------|---------|--------|
| Again | Forgot completely | Reset interval |
| Hard | Correct with difficulty | Short interval |
| Good | Correct with hesitation | Normal interval |
| Easy | Perfect recall | Long interval |

The algorithm adjusts review timing based on your performance. Cards you know well appear less often; cards you struggle with appear more frequently.

### Data Storage

Study data is stored locally. The location is auto-detected:

| Environment | Path |
|---|---|
| OpenClaw / ClawdBot | `~/.openclaw/workspace/study-data/` |
| Claude Desktop / Other | `~/.study-buddy/data/` |
| Custom | Set `STUDY_DATA_DIR` env var |

```
study-data/
├── decks.json          # Deck index & global stats
└── {deck-id}.json      # Individual deck cards with SR data
```

## File Structure

```
study-buddy-skill/
├── SKILL.md                    # Main skill instructions (read this first)
├── AGENTS.md                   # Quick-reference for Codex agents
├── assets/
│   ├── quiz.html               # Interactive quiz template
│   ├── flashcards.html         # Flashcard flip template
│   ├── dashboard.html          # Study progress dashboard
│   └── setup.html              # Studium connection wizard
├── scripts/
│   ├── study_manager.py        # Core logic (SM-2, decks, cards)
│   └── studium_quiz.py         # Canvas LMS integration
├── references/
│   └── question-patterns.md    # Bloom's taxonomy question templates
├── .env.studium.example        # Template for Canvas API credentials
└── .gitignore
```

## Canvas LMS Integration

Connect to Studium or any Canvas instance:

1. Go to your Canvas settings and generate an API token
2. Tell Claude "Connect to Studium" — it will save the token locally
3. Ask "Quiz me on my latest lecture" — it fetches content and generates questions

Or set it up manually:

```bash
cp .env.studium.example .env.studium
# Edit .env.studium and add your token
```

See the setup wizard in `assets/setup.html` for step-by-step instructions.

## Privacy

- ✅ **100% Local** — All data stays on your machine
- ✅ **No Servers** — No cloud, no accounts required
- ✅ **Open Source** — Audit the code yourself
- ✅ **Your Data** — Export or delete anytime

## License

MIT License — use it however you want.

---

Made with 🧠 by [Birger Moell](https://github.com/birgermoell)
