
## 2024-05-20 - Caching Filesystem Scans

**Learning:** The application frequently performs expensive filesystem scans in API endpoints, such as listing wallpapers. The `get_random_wallpaper` function was repeatedly scanning the same directory, causing unnecessary I/O and slowing down the response time. Caching the results of these scans in memory is a highly effective optimization.

**Action:** For any new or existing endpoints that read from the filesystem, I will evaluate if the data can be cached. If the underlying files change infrequently, I will implement a caching mechanism like `@lru_cache` to reduce redundant I/O and improve performance.
