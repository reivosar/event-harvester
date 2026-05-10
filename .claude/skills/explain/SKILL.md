---
name: explain
description: Explain a piece of code, function, file, or concept clearly. Use this skill when the user asks "what does X do?", "how does this work?", "explain this to me", "walk me through this code", or pastes code and seems confused. Also use it proactively when the user is about to modify something complex and understanding it first would help.
---

# Explain

Explain the target clearly to someone who hasn't seen it before.

## Arguments

The target is `$ARGUMENTS` — a file path, function name, concept, or pasted code.

## Before explaining

If the target is a file path or symbol name, read the code before saying anything. A confident-sounding wrong explanation is worse than saying "let me look at this first."

```bash
# Find the definition if the path isn't given
grep -rn "functionName" src/ --include="*.ts"
```

## Structure

**1. One sentence**
What is this thing? Answer in one sentence at the level of what it *does*, not how it does it.

> `AuthMiddleware` validates the JWT on every incoming request and attaches the decoded user to the request context.

**2. How it works**
Walk through the logic step by step, referencing specific lines or sections. Use concrete values in examples rather than abstract placeholders — "if `user.role` is `"admin"`" is easier to follow than "if the role field matches a privileged value."

**3. Why it's built this way**
What constraint or decision led to this design? If it's non-obvious, explain the tradeoff. If you genuinely can't tell, say so — "I'm not sure why this wasn't done with X instead, it may be historical."

**4. What to watch out for**
What does a caller, maintainer, or someone modifying this code need to know? Side effects, preconditions, known edge cases, things that are easy to break by accident.

## Calibrate to the audience

Read the conversation for cues about the user's background. A senior engineer asking about an unfamiliar subsystem needs different depth than someone learning to code. Match the vocabulary accordingly.
