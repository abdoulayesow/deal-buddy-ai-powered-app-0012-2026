# Generate Session Summary

Run the summary-generator skill to create a session summary and resume prompt.

## Instructions

1. **Read the skill**: `.skills/summary-generator/SKILL.md`
2. **Analyze work**: Run `git status`, `git diff --stat`, `git log --oneline -10`
3. **Generate summary**: Create `docs/summaries/YYYY-MM-DD_feature-name.md` using `.skills/summary-generator/TEMPLATE.md`
4. **Include**:
   - Overview, Completed Work, Key Files Modified
   - Design Patterns Used
   - Remaining Tasks / Next Steps
   - **Resume Prompt** (must start with token optimization directive from `.skills/summary-generator/guidelines/token-optimization.md`)
5. **Output**: Provide the resume prompt as copy-paste ready text for the next session

## Resume Prompt Requirements

The resume prompt MUST start with:

```
IMPORTANT: Follow token optimization patterns from `.skills/summary-generator/guidelines/token-optimization.md`:
- Use Grep before Read for searches
- Use Explore agent for multi-file exploration
- Reference this summary instead of re-reading files
- Keep responses concise
```

Then include: Context, Key Files to Review, Current Status, Next Steps, Important Notes.
