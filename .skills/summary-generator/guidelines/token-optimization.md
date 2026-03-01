# Token Optimization Guidelines

## Overview

These guidelines help reduce token usage while maintaining quality and effectiveness. The goal is to be efficient without compromising on clarity or thoroughness.

## Core Principles

1. **Read Once, Reference Often** - Cache information in conversation context
2. **Search Before Reading** - Use Grep/Glob to target specific content
3. **Be Concise Yet Complete** - Clear and brief without losing substance
4. **Avoid Redundancy** - Don't repeat what's already been established
5. **Use Documentation** - Reference CLAUDE.md and project docs

## File Reading Optimization

### DO: Use Targeted Searches

**Pattern: Grep then Read Specific Section**
```
1. Grep pattern="functionName" path="src/"
2. Read src/services/advisory.ts offset=50 limit=20
```

**Why:** Only loads the relevant portion, not entire file

**Pattern: Use offset/limit for Large Files**
```
Read prisma/schema.prisma offset=100 limit=100  # Specific model
```

**Why:** Avoids loading thousands of lines when you need dozens

### DON'T: Read Full Files Repeatedly

**Anti-Pattern: Multiple Full Reads**
```
Read prisma/schema.prisma  # 500 lines loaded
... 30 minutes later ...
Read prisma/schema.prisma  # Same 500 lines loaded again
```

**Better:**
```
Read prisma/schema.prisma  # First read
... later ...
Grep pattern="User" path="prisma/schema.prisma"  # Just check field exists
```

### DON'T: Read Generated Files

**Anti-Pattern: Reading Build Artifacts**
```
Read node_modules/@anthropic-ai/sdk/index.d.ts
Read dist/index.js
```

**Why:** These are large, generated, and rarely useful. Use documentation instead.

## Search Pattern Optimization

### DO: Combine Patterns

**Pattern: Use Brace Expansion**
```
Glob pattern="src/**/*.{ts,tsx}"
```

**Why:** One search instead of multiple

**Pattern: Use Appropriate Scope**
```
Grep pattern="sendMessage" path="src/services/" type="ts"
```

**Why:** Searches only relevant directory and file type

### DON'T: Sequential Similar Searches

**Anti-Pattern: Multiple Similar Globs**
```
Glob pattern="**/*.ts"
Glob pattern="**/*.tsx"
```

**Better:**
```
Glob pattern="**/*.{ts,tsx}"
```

## Response Optimization

### DO: Be Concise

**Pattern: Direct and Clear**
```
"Fixed webhook handler to return 200 before processing message"
```

**Pattern: Bullets Over Paragraphs**
```
Updated the onboarding flow:
- Added region detection from WhatsApp location pin
- Maps to 14 Senegal regions
- Stores in user profile for personalized advice
```

### DON'T: Over-Explain Simple Tasks

**Anti-Pattern: Verbose Explanation**
```
"I notice there's an error in the webhook handler. The handler is not returning a 200 status code quickly enough, which causes WhatsApp to retry the message. After investigating the code, I found that we need to acknowledge receipt immediately before processing..."
```

**Better:**
```
"Fixed: webhook now returns 200 immediately, processes message asynchronously"
```

## Agent Usage Optimization

### DO: Use Agents for Complex Tasks

**Pattern: Explore Agent for Codebase Understanding**
```
Task: Use Explore agent to understand message processing pipeline
- Agent performs multiple searches
- Agent reads multiple files
- Returns synthesized understanding
```

**Why:** One agent spawn is cheaper than you doing 10 searches manually

### DON'T: Spawn Agents for Simple Lookups

**Anti-Pattern: Agent for Single File**
```
Task: Use Explore agent to find if schema.prisma has User model
```

**Better:**
```
Grep pattern="model User" path="prisma/schema.prisma"
```

## Code Generation Optimization

### DO: Generate Complete, Correct Code

**Pattern: One-Shot Implementation**
```
Write complete service with:
- All imports
- Full type definitions
- Complete implementation
- No placeholders
```

**Why:** Generating once is cheaper than generating, fixing, regenerating

**Pattern: Read Types Before Implementing**
```
1. Read existing type definitions
2. Generate new code matching patterns
3. No type errors, no rework
```

### DON'T: Generate Incrementally for Simple Code

**Anti-Pattern: Multiple Small Generations**
```
1. Generate function signature
2. Generate function body
3. Generate type definition
```

**Better:**
```
1. Generate complete function with types and implementation
```

## Practical Guidelines

### Before Each Action

Ask yourself:
1. **Do I need to read this file?** Could Grep answer my question?
2. **Have I already read this?** Can I reference earlier context?
3. **Is this the minimal search?** Can I narrow the scope?
4. **Is this explanation necessary?** Is it self-evident?
5. **Can I combine operations?** Multiple patterns in one call?

### Token Budget Awareness

Think of tokens as a budget:
- **Large Files:** 500-5000 tokens each
- **Agent Spawns:** 500-10,000 tokens
- **Code Generation:** 200-2000 tokens
- **Explanations:** 100-500 tokens
- **Simple Responses:** 20-100 tokens

Spend wisely on what adds most value.

### Quality vs Efficiency

**Never Sacrifice:**
- Correctness
- Security
- User clarity
- Critical explanations

**Always Optimize:**
- Redundant operations
- Unnecessary verbosity
- Repeated searches
- Over-documentation

## Efficiency Checklist

**File Operations:**
- [ ] Used Grep before Read when searching
- [ ] Used offset/limit for large files
- [ ] Avoided re-reading same file
- [ ] Didn't read generated/build files

**Search Operations:**
- [ ] Combined similar patterns
- [ ] Scoped to relevant directories
- [ ] Used appropriate file type filters

**Responses:**
- [ ] Kept responses concise
- [ ] Used bullets over paragraphs
- [ ] Referenced earlier explanations
- [ ] Avoided narrating actions

**Code Generation:**
- [ ] Read types/patterns first
- [ ] Generated complete code
- [ ] Avoided incremental generation
- [ ] Minimized rework

## Target Efficiency

**Aim for:**
- Efficiency Score: 85+
- <10% redundant operations
- <5 duplicate file reads
- Concise responses (<200 chars for simple tasks)
- High first-attempt success rate

## Remember

Efficiency is about **maximizing value per token**, not minimizing explanation or rushing through work. Take time to plan, ask questions, and understand requirements—this prevents costly rework later.
