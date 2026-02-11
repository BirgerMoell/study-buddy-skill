# Question Generation Patterns

## Bloom's Taxonomy Levels

Generate questions across cognitive levels:

### 1. Remember (Recall facts)
- "What is...?"
- "Define..."
- "List the..."
- "When did...?"

### 2. Understand (Explain concepts)
- "Explain why..."
- "What is the difference between X and Y?"
- "Summarize..."
- "Give an example of..."

### 3. Apply (Use in new situations)
- "How would you use X to...?"
- "Calculate..."
- "Demonstrate..."
- "What would happen if...?"

### 4. Analyze (Break down)
- "What are the components of...?"
- "Compare and contrast..."
- "What is the relationship between...?"
- "What evidence supports...?"

### 5. Evaluate (Judge/justify)
- "Which is more effective...?"
- "What are the pros and cons of...?"
- "Do you agree that...? Why?"
- "What is the most important...?"

### 6. Create (Produce new)
- "Design a..."
- "How could you improve...?"
- "What alternative would you suggest?"

## Question Type Templates

### Multiple Choice
```json
{
  "question": "[Stem that poses a clear problem]",
  "options": [
    "[Correct answer]",
    "[Plausible distractor 1]",
    "[Plausible distractor 2]",
    "[Plausible distractor 3]"
  ],
  "correct": 0,
  "explanation": "[Why correct answer is right]"
}
```

**Distractor strategies:**
- Common misconceptions
- Partially correct answers
- Answers that would be correct for a different question
- Reversed or inverted correct answers

### True/False
```json
{
  "question": "[Clear declarative statement]",
  "options": ["True", "False"],
  "correct": 0,
  "explanation": "[Clarification]"
}
```

**Tips:**
- Avoid absolute words (always, never) unless testing that knowledge
- One concept per statement
- Avoid double negatives

### Fill-in-the-Blank (as MC)
```json
{
  "question": "The process by which plants convert sunlight into energy is called ___.",
  "options": ["photosynthesis", "respiration", "fermentation", "digestion"],
  "correct": 0
}
```

### Matching (as series of MC)
For matching A→1, B→2, C→3, create individual questions:
```json
{
  "question": "Match: Term A corresponds to:",
  "options": ["Definition 1", "Definition 2", "Definition 3"],
  "correct": 0
}
```

## Flashcard Patterns

### Definition Cards
- Front: Term
- Back: Definition

### Concept Cards
- Front: "What is [concept]?"
- Back: Explanation

### Process Cards
- Front: "What are the steps of [process]?"
- Back: Numbered steps

### Comparison Cards
- Front: "How does X differ from Y?"
- Back: Key differences

### Application Cards
- Front: "When would you use [technique]?"
- Back: Use cases

### Example Cards
- Front: "Give an example of [concept]"
- Back: Concrete example

## Content-to-Question Extraction

### From Definitions
> "Photosynthesis is the process by which plants convert light energy into chemical energy."

→ Flashcard: "Photosynthesis" / "Process by which plants convert light energy into chemical energy"
→ MC: "What is photosynthesis?" + options

### From Lists
> "The three branches of government are: legislative, executive, and judicial."

→ Flashcard: "Three branches of government" / "Legislative, Executive, Judicial"
→ MC: "Which is NOT a branch of government?" + [legislative, executive, judicial, administrative]

### From Comparisons
> "Unlike DNA, RNA is single-stranded and contains uracil instead of thymine."

→ Flashcard: "Difference between DNA and RNA" / "RNA is single-stranded, has uracil; DNA is double-stranded, has thymine"
→ MC: "What base does RNA have that DNA does not?" + [uracil, thymine, adenine, cytosine]

### From Cause-Effect
> "Global warming causes sea levels to rise due to thermal expansion and ice melt."

→ Flashcard: "Why does global warming raise sea levels?" / "Thermal expansion and melting ice"
→ MC: "Which is a cause of sea level rise due to global warming?" + options

## Quality Checklist

Before presenting questions:

- [ ] Clear, unambiguous wording
- [ ] One correct answer (for MC)
- [ ] Distractors are plausible but clearly wrong
- [ ] No grammatical clues to correct answer
- [ ] Appropriate difficulty for audience
- [ ] Tests meaningful knowledge (not trivia)
- [ ] Explanation provided for learning
