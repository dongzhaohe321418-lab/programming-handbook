"""Execute every ```python code block in docs/ and check it behaves as marked.

This mirrors what the in-browser Run button does (Pyodide executes the block),
so a green suite means every Run button on the site works.

First-line markers understood (see WRITING_GUIDE.md):

- ``# raises SomeError`` — the block must raise an exception whose type name
  matches (teaching tracebacks is a feature, not a failure).
- ``# widget``  — bound to page sliders; skipped here.
- ``# no-test`` — explicitly excluded from CI.
- ``# continues`` — executed in the page's shared namespace (it builds on the
  blocks above it). All other blocks must be fully self-contained and are run
  in a fresh namespace.
"""
from __future__ import annotations

import re
import signal
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DOCS = Path(__file__).resolve().parent.parent / "docs"
BLOCK_TIMEOUT_S = 30

FENCE_OPEN = re.compile(r"^(\s*)```python(\s+[^`]*)?\s*$")


def extract_blocks(md_path: Path):
    """Yield (start_line, dedented_code) for each ```python fence."""
    lines = md_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        m = FENCE_OPEN.match(lines[i])
        if not m:
            i += 1
            continue
        indent = m.group(1)
        close = re.compile(r"^" + re.escape(indent) + r"```\s*$")
        body: list[str] = []
        j = i + 1
        while j < len(lines) and not close.match(lines[j]):
            line = lines[j]
            body.append(line[len(indent):] if line.startswith(indent) else line)
            j += 1
        yield i + 1, "\n".join(body)
        i = j + 1


def collect_cases():
    cases = []
    for md in sorted(DOCS.rglob("*.md")):
        rel = md.relative_to(DOCS)
        for lineno, code in extract_blocks(md):
            cases.append(pytest.param(md, code, id=f"{rel}:{lineno}"))
    return cases


CASES = collect_cases()

# Per-page namespaces so `# continues` blocks can build on earlier blocks.
_PAGE_NS: dict[Path, dict] = {}


class _Timeout(Exception):
    pass


def _alarm(_sig, _frm):
    raise _Timeout(f"block exceeded {BLOCK_TIMEOUT_S}s")


def run_block(code: str, ns: dict) -> None:
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(BLOCK_TIMEOUT_S)
    try:
        exec(compile(code, "<snippet>", "exec"), ns)  # noqa: S102
    finally:
        signal.alarm(0)
        plt.close("all")


@pytest.mark.parametrize("md_path,code", CASES)
def test_snippet(md_path: Path, code: str):
    first = code.lstrip().splitlines()[0].strip() if code.strip() else ""
    if first.startswith("# widget") or first.startswith("# no-test"):
        pytest.skip("marked as browser-only")

    page_ns = _PAGE_NS.setdefault(md_path, {"__name__": "__main__"})

    expected = None
    m = re.match(r"#\s*raises\s+(\w+)", first)
    if m:
        expected = m.group(1)

    if expected:
        with pytest.raises(Exception) as excinfo:
            run_block(code, {"__name__": "__main__"})
        actual = type(excinfo.value).__name__
        assert actual == expected or expected in repr(excinfo.value), (
            f"expected {expected}, got {actual}: {excinfo.value!r}"
        )
        return

    if first.startswith("# continues"):
        run_block(code, page_ns)
        return

    # Self-contained block: must run alone in a fresh namespace …
    run_block(code, {"__name__": "__main__"})
    # … and also feed the page namespace for any `# continues` block below.
    try:
        run_block(code, page_ns)
    except Exception:  # noqa: BLE001 — page-ns replay is best-effort
        pass
