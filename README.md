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

## Quick Start

### OpenClaw / Clawdbot

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/birgermoell/study-buddy-skill.git study-buddy
```

That's it! Just ask: *"Create flashcards for..."*

### Claude Desktop (MCP)

```bash
git clone https://github.com/birgermoell/study-buddy-skill.git
cd study-buddy-skill
pip install -e ".[mcp]"
```

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "study-buddy": {
      "command": "python3",
      "args": ["/path/to/study-buddy-skill/src/mcp_server.py"]
    }
  }
}
```

### Codex CLI

```bash
git clone https://github.com/birgermoell/study-buddy-skill.git
```

Reference in your `AGENTS.md`:

```markdown
## External Skills
- [Study Buddy](./study-buddy-skill/AGENTS.md) - Flashcards & Quizzes
```

## Usage Examples

```
"Make flashcards for these terms: photosynthesis, mitosis, osmosis"

"Quiz me on Chapter 5"

"What cards are due for review?"

"Show my study dashboard"

"Create a deck from my latest Studium lecture"
```

## How It Works

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

All data is stored locally in `~/.openclaw/workspace/study-data/`:

```
study-data/
├── decks.json          # Deck index & global stats
└── {deck-id}.json      # Individual deck cards
```

## File Structure

```
study-buddy-skill/
├── SKILL.md                    # Agent instructions
├── scripts/
│   ├── study_manager.py        # Core logic (SM-2, decks, cards)
│   └── studium_quiz.py         # Canvas LMS integration
├── assets/
│   ├── dashboard.html          # Study dashboard UI
│   ├── quiz.html               # Quiz interface
│   └── flashcards.html         # Flashcard interface
└── references/
    └── question-patterns.md    # Question generation patterns
```

## Canvas LMS Integration

Connect to Studium or any Canvas instance:

```bash
# Set credentials
echo 'STUDIUM_API_KEY=your_token' > ~/.openclaw/workspace/.env.studium
echo 'STUDIUM_BASE_URL=https://uppsala.instructure.com' >> ~/.openclaw/workspace/.env.studium

# Then just ask:
"Quiz me on my latest lecture"
```

See [studium-skill](https://github.com/birgermoell/studium-skill) for Canvas API setup.

## Privacy

- ✅ **100% Local** — All data stays on your machine
- ✅ **No Servers** — No cloud, no accounts required
- ✅ **Open Source** — Audit the code yourself
- ✅ **Your Data** — Export or delete anytime

## License

MIT License — use it however you want.

---

Made with 🧠 by [Birger Moëll](https://github.com/birgermoell)
