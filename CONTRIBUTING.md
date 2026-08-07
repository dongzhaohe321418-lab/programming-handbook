# Contributing

Thank you for helping improve the Programming & Computer Systems Handbook!

## Found a mistake?

Open an issue at
<https://github.com/dongzhaohe321418-lab/programming-handbook/issues> with the
page URL and what's wrong. Factual errors in code or complexity claims are
top priority.

## Pull requests

1. Fork, branch, edit the Markdown under `docs/`.
2. Read `WRITING_GUIDE.md` first — it defines page anatomy and, crucially,
   the contract for runnable Python blocks (self-contained, stdlib + numpy +
   matplotlib only, `# raises` / `# widget` / `# continues` markers).
3. Verify locally:

   ```bash
   pip install -r requirements.txt pytest numpy matplotlib
   mkdocs build --strict        # no broken links/nav
   python -m pytest tests/ -q   # every snippet must run
   ```

4. Open a PR with a short description of what changed and why.

## Scope

The handbook follows a standard Programming I → Programming II arc plus
computer-systems context. New sections should fit an existing chapter; propose
new chapters in an issue first.
