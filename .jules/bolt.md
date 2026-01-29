## 2024-05-23 - Filesystem Iteration Caching
**Learning:** Repeatedly calling `glob` or `iterdir` on the filesystem for static content (like wallpaper packs) creates unnecessary I/O overhead.
**Action:** Use `functools.lru_cache` to cache the results of filesystem scans for read-heavy endpoints, and use `pathlib` efficiently (e.g., checking suffix before `is_file()` stat calls).
