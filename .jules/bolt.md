# Bolt's Journal ⚡

This journal is for CRITICAL, codebase-specific performance learnings.

## 2024-07-29 - Filesystem Caching for Repeated Lookups

**Learning:** The application was repeatedly scanning the filesystem to list images within wallpaper packs, causing significant I/O overhead and latency on every request to endpoints like `/api/wallpapers/shuffle/<pack_name>`. Using a simple in-memory cache (`@lru_cache`) on a helper function that performs the scan is a highly effective way to mitigate this.

**Action:** For any future development involving repeated reads from the filesystem for data that changes infrequently, apply a caching layer (e.g., `lru_cache` or a time-based cache) to memoize the results. This pattern should be the default for file-based metadata lookups.
