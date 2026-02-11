#!/usr/bin/env python3
"""
Studium Quiz Generator - Fetch content from Studium and prepare for quiz/flashcard generation.

This script bridges the Studium skill with the Study Buddy skill.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error

# Add studium skill to path
WORKSPACE = Path.home() / ".openclaw" / "workspace"
sys.path.insert(0, str(WORKSPACE / "skills" / "studium" / "scripts"))

BASE_URL = os.environ.get("STUDIUM_BASE_URL", "https://uppsala.instructure.com")
API_KEY = os.environ.get("STUDIUM_API_KEY", "")


def api_get(endpoint: str) -> dict:
    """Make authenticated GET request to Canvas API."""
    url = f"{BASE_URL}/api/v1/{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.reason}", file=sys.stderr)
        return {}


def get_courses(enrollment_state: str = "active") -> list:
    """Get user's courses."""
    return api_get(f"courses?enrollment_state={enrollment_state}&per_page=50")


def get_recent_modules(course_id: int, limit: int = 5) -> list:
    """Get recent module items from a course."""
    modules = api_get(f"courses/{course_id}/modules?per_page=10")
    
    items = []
    for module in modules[:3]:  # Check first 3 modules
        module_items = api_get(f"courses/{course_id}/modules/{module['id']}/items?per_page=20")
        items.extend(module_items)
    
    # Sort by position (most recent last in modules usually)
    return items[-limit:] if items else []


def get_pages(course_id: int, limit: int = 5) -> list:
    """Get recent pages from a course."""
    pages = api_get(f"courses/{course_id}/pages?sort=updated_at&order=desc&per_page={limit}")
    return pages


def get_page_content(course_id: int, page_url: str) -> str:
    """Get full content of a page."""
    page = api_get(f"courses/{course_id}/pages/{page_url}")
    return page.get("body", "")


def get_assignments(course_id: int, limit: int = 5) -> list:
    """Get recent assignments."""
    assignments = api_get(f"courses/{course_id}/assignments?order_by=due_at&per_page={limit}")
    return assignments


def get_assignment_content(course_id: int, assignment_id: int) -> dict:
    """Get assignment details including description."""
    return api_get(f"courses/{course_id}/assignments/{assignment_id}")


def get_announcements(course_id: int, limit: int = 5) -> list:
    """Get recent announcements."""
    return api_get(f"courses/{course_id}/discussion_topics?only_announcements=true&per_page={limit}")


def find_latest_lecture_content(course_id: int = None) -> dict:
    """
    Find the most recent lecture/learning content from a course.
    
    Returns dict with:
        - title: Content title
        - content: Text content for quiz generation
        - source: Where it came from (page, module, assignment)
        - course: Course name
    """
    if not API_KEY:
        return {"error": "STUDIUM_API_KEY not set"}
    
    # If no course specified, get most recently accessed
    if not course_id:
        courses = get_courses()
        if not courses:
            return {"error": "No courses found"}
        # Sort by last activity or just take first active
        course = courses[0]
        course_id = course["id"]
        course_name = course.get("name", "Unknown Course")
    else:
        course = api_get(f"courses/{course_id}")
        course_name = course.get("name", "Unknown Course")
    
    result = {
        "course_id": course_id,
        "course": course_name,
        "items": []
    }
    
    # Try pages first (often lecture notes)
    pages = get_pages(course_id, limit=3)
    for page in pages:
        content = get_page_content(course_id, page["url"])
        if content and len(content) > 200:  # Minimum content
            result["items"].append({
                "type": "page",
                "title": page.get("title", "Untitled"),
                "content": strip_html(content),
                "updated": page.get("updated_at")
            })
    
    # Try recent assignments
    assignments = get_assignments(course_id, limit=3)
    for assignment in assignments:
        desc = assignment.get("description", "")
        if desc and len(desc) > 200:
            result["items"].append({
                "type": "assignment", 
                "title": assignment.get("name", "Untitled"),
                "content": strip_html(desc),
                "due": assignment.get("due_at")
            })
    
    # Sort by recency and pick best
    if result["items"]:
        result["latest"] = result["items"][0]
    
    return result


def strip_html(html: str) -> str:
    """Simple HTML tag stripping."""
    import re
    # Remove script/style
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Decode entities
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text


def generate_flashcard_prompts(content: str, title: str) -> str:
    """
    Generate a prompt for the LLM to create flashcards from content.
    """
    return f"""Generate flashcards from this lecture content. Create 10-15 cards covering the key concepts.

**Lecture: {title}**

{content[:4000]}

---

Return JSON array of flashcards:
```json
[
  {{"front": "Question or term", "back": "Answer or definition"}},
  ...
]
```

Focus on:
- Key definitions and concepts
- Important relationships
- Facts worth remembering
- Application scenarios

Keep cards atomic (one concept each). Front should be a clear question or term. Back should be concise but complete."""


def generate_quiz_prompts(content: str, title: str, num_questions: int = 10) -> str:
    """
    Generate a prompt for the LLM to create quiz questions from content.
    """
    return f"""Generate a {num_questions}-question multiple choice quiz from this lecture content.

**Lecture: {title}**

{content[:4000]}

---

Return JSON array of questions:
```json
[
  {{
    "question": "Clear question text",
    "options": ["Correct answer", "Plausible wrong 1", "Plausible wrong 2", "Plausible wrong 3"],
    "correct": 0,
    "explanation": "Brief explanation why this is correct"
  }},
  ...
]
```

Guidelines:
- Mix difficulty levels (easy recall → harder application)
- All options should be plausible
- Correct answer should be at index 0 (will be shuffled)
- Cover the main concepts from the lecture"""


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch Studium content for quiz generation")
    parser.add_argument("command", choices=["courses", "latest", "content", "prompt"])
    parser.add_argument("--course", type=int, help="Course ID")
    parser.add_argument("--type", choices=["flashcards", "quiz"], default="flashcards")
    
    args = parser.parse_args()
    
    if args.command == "courses":
        courses = get_courses()
        for c in courses:
            print(f"{c['id']}: {c.get('name', 'Unnamed')}")
    
    elif args.command == "latest":
        result = find_latest_lecture_content(args.course)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == "prompt":
        result = find_latest_lecture_content(args.course)
        if "latest" in result:
            item = result["latest"]
            if args.type == "flashcards":
                print(generate_flashcard_prompts(item["content"], item["title"]))
            else:
                print(generate_quiz_prompts(item["content"], item["title"]))
        else:
            print("No content found", file=sys.stderr)
