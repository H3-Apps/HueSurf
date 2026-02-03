## 2025-05-14 - Optimized Wallpaper Filesystem Scanning
**Learning:** Multiple calls to `Path.glob()` and `Path.rglob()` on the same directory cause redundant filesystem traversals and syscalls. Consolidating these into a single-pass `rglob("*")` or `os.scandir` combined with `lru_cache` provides significant performance wins, especially when dealing with static assets.
**Action:** Use a single-pass helper function with memoization for any logic that needs to categorize or count files in a directory.
