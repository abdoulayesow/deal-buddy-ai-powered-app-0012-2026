# Command Accuracy Guidelines

## Overview

These guidelines help improve first-attempt success rate and reduce failed commands. The goal is to execute commands correctly the first time through verification and best practices.

## Core Principles

1. **Verify Before Executing** - Check assumptions before running commands
2. **Follow Existing Patterns** - Match what already works in the codebase
3. **Read Definitions First** - Understand types/interfaces before implementing
4. **Use Cross-Platform Paths** - Always use forward slashes
5. **Test Incrementally** - Validate each step before proceeding

## Path Accuracy

### DO: Use Forward Slashes

**Pattern: Cross-Platform Paths**
```
src/routes/webhook.ts
prisma/schema.prisma
.claude/skills/summary-generator/SKILL.md
```

**Why:** Works on Windows, macOS, and Linux consistently

**Pattern: Verify Path Exists**
```
1. Glob pattern="src/routes/webhook*"
2. Read src/routes/webhook.ts
```

**Why:** Confirms file exists and gets exact path/case

### DON'T: Use Backslashes

**Anti-Pattern: Windows-Style Paths**
```
src\routes\webhook.ts
prisma\schema.prisma
```

**Why:** Fails in most tools, only works in Windows cmd

### Case Sensitivity

**Pattern: Match Exact Case**
```
1. Glob finds: src/services/whatsapp.ts
2. Read src/services/whatsapp.ts  # Exact match
```

**Why:** Linux is case-sensitive; wrong case = file not found

## Import Path Accuracy

### DO: Check Existing Imports

**Pattern: Grep for Existing Usage**
```
# Before using an import, check how others use it
Grep pattern="import.*prisma" path="src/services"

# Results show: import { prisma } from '../lib/prisma'
# Now use the same path
```

**Why:** Confirms correct import path and usage pattern

**Pattern: Verify Module Exports**
```
# Check what a module exports
Read src/lib/prisma.ts

# See: export const prisma = new PrismaClient()
# Use: import { prisma } from '../lib/prisma'
```

**Why:** Ensures you're importing what actually exists

### DON'T: Guess Import Paths

**Anti-Pattern: Assumption Without Verification**
```
import { prisma } from '@/lib/prisma'  # Guessed alias
# Error: Module not found

# Should have checked existing files first
```

## Type Safety

### DO: Read Interfaces First

**Pattern: Understand Types Before Implementing**
```
# Before creating a new service, read existing types
Read src/types/whatsapp.ts

# See interface WhatsAppMessage { ... }
# Match this in new handler
```

**Why:** Prevents type mismatches and refactoring

### DON'T: Assume Type Structure

**Anti-Pattern: Guessing Interface Shape**
```
interface User {
  phone: string  # Guessed
}

# But existing code uses:
interface User {
  phoneNumber: string
}
```

**Prevention:**
1. Read existing type definitions
2. Check how existing code uses types
3. Match established patterns

## Edit Tool Accuracy

### DO: Copy Exact Strings

**Pattern: Read Then Edit**
```
1. Read file.ts lines 10-20
   # Output shows:
   # 15→  const user = await findUser(phone)

2. Edit file.ts
   old_string: "  const user = await findUser(phone)"  # Exact copy
   new_string: "  const user = await findUser(phoneNumber)"
```

**Why:** Exact match prevents "string not found" errors

**Pattern: Include Enough Context**
```
# If old_string appears multiple times, add more context
old_string: `app.post('/webhook', async (c) => {
  const body = await c.req.json()
  const user = await findUser(phone)`

# Instead of just: "const user = await findUser(phone)"
```

**Why:** Makes the match unique in the file

### DON'T: Modify Whitespace

**Anti-Pattern: Changing Indentation**
```
Read output shows: "  const user = findUser(phone)"  # 2 spaces
Edit uses: "    const user = findUser(phone)"  # 4 spaces

# Result: String not found error
```

**Prevention:** Copy exactly from Read output, including whitespace

## Hono Route Accuracy

### DO: Match Hono Patterns

**Pattern: Check Existing Routes**
```
# Check existing route handlers first
Grep pattern="app\.(get|post|put|delete)" path="src/routes"

# See pattern and match it exactly
```

**Pattern: Verify Middleware**
```
# Check what middleware is used
Grep pattern="import.*hono" path="src/routes"
```

### DON'T: Use Wrong Framework Patterns

**Anti-Pattern: Express-style in Hono**
```
app.post('/webhook', (req, res) => {  # Express pattern
  res.json({ status: 'ok' })
})
```

**Correct Hono pattern:**
```
app.post('/webhook', async (c) => {  # Hono pattern
  return c.json({ status: 'ok' })
})
```

## Verification Checklist

Before executing each command, verify:

### For Read Operations
- [ ] Path uses forward slashes
- [ ] File path exists (Glob to verify)
- [ ] Case matches exactly
- [ ] Not reading generated files (node_modules, dist)

### For Edit Operations
- [ ] Recently read the file
- [ ] Copied old_string exactly from Read output
- [ ] Included enough context if not unique
- [ ] Preserved exact whitespace/indentation
- [ ] New string is different from old string

### For Write Operations
- [ ] Parent directory exists
- [ ] Not overwriting existing file (should use Edit)
- [ ] Path uses forward slashes

### For Import Statements
- [ ] Grepped for existing imports in similar files
- [ ] Verified module exports (default vs named)
- [ ] Used correct path (relative or alias)
- [ ] Import style matches export style

### For Type Usage
- [ ] Read interface/type definitions
- [ ] Checked existing usage
- [ ] Property names are correct
- [ ] Type structure matches codebase

## Common Error Prevention

### Path Errors
**Prevention Steps:**
1. Always use forward slashes
2. Glob to verify file exists
3. Match exact case from Glob results
4. Check parent directory exists (for Write)

### Import Errors
**Prevention Steps:**
1. Grep for existing imports in similar files
2. Read module to check export style
3. Use same import pattern as existing code
4. Verify module path exists

### Type Errors
**Prevention Steps:**
1. Read interface definitions before implementing
2. Check how existing code uses types
3. Match property names exactly
4. Verify optional vs required fields

### Edit Errors
**Prevention Steps:**
1. Read file immediately before editing
2. Copy old_string exactly (including whitespace)
3. Include enough context to be unique
4. Test with small changes first

## Recovery Strategies

When a command fails:

### Immediate Actions
1. **Read the error message carefully** — Identifies exact issue
2. **Check assumptions** — Verify file path, import path, type expectations
3. **Look for existing patterns** — How do other files handle this?

### Quick Fixes
- **Path error:** Glob to find correct path
- **Import error:** Grep to find correct import
- **Type error:** Read type definition
- **Edit error:** Re-read file for exact string

## Success Metrics

Target accuracy metrics:

**Overall:**
- Success Rate: 95%+
- Critical Errors: 0
- High-Severity Errors: <2 per session

**By Category:**
- Path Errors: <1 per session
- Import Errors: <1 per session
- Type Errors: <2 per session
- Edit Errors: <1 per session

## Best Practices Summary

1. **Always verify paths** with Glob before Read/Edit/Write
2. **Always check existing patterns** before implementing
3. **Always read type definitions** before using types
4. **Always use forward slashes** in all paths
5. **Always copy exactly** when using Edit tool
6. **Always grep for imports** before adding new ones
7. **Always test incrementally** rather than all at once
8. **Always learn from errors** and update patterns

## Remember

The goal is **getting it right the first time** through:
- Verification before execution
- Following existing patterns
- Understanding types and interfaces
- Using cross-platform conventions
- Learning from each error

Spending 30 seconds to verify is better than spending 5 minutes fixing errors.
