## 2026-02-02 - Caching I/O bound wallpaper metadata
**Learning:** Repetitive filesystem globbing and JSON parsing in Flask endpoints (like shuffling or previewing) can be a significant bottleneck, especially when scaling. Using `@lru_cache` on granular helper functions is an effective, low-complexity solution.
**Action:** Always wrap filesystem-heavy operations in cached helpers. Ensure cache invalidation is handled in any endpoint that modifies the source data (e.g., `/repack`).
