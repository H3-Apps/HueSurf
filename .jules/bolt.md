## 2026-01-31 - [Wallpaper Metadata Optimization]
**Learning:** Repetitive `glob()` calls and recursive `rglob("*")` scans in a Flask app significantly degrade performance (e.g., ~178ms for just 2 packs). Using `pathlib.Path.iterdir()` in a single pass combined with `functools.lru_cache` can reduce response times by over 50%.
**Action:** Replace multiple directory scans with a single-pass helper function and use `lru_cache` for I/O-heavy metadata retrieval.
