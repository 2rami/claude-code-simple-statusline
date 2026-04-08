Debug this issue systematically:

1. Reproduce — understand expected vs actual behavior
2. Isolate — narrow down to the specific file and function
3. Root cause — read error messages, check git diff, trace the logic
4. Fix — implement the minimal correct fix, nothing more
5. Verify — confirm the fix works and check for regressions

Rules:
- Never guess. Read the error first.
- Check recent changes with git log / git diff.
- One fix at a time — don't change multiple things simultaneously.
