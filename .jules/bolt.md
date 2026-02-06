## 2025-05-14 - [Cached Single-Pass Traversals]
**Learning:** Redundant filesystem traversals (using multiple `glob` or `rglob` calls) are a major bottleneck when dealing with assets. Consolidating these into a single pass with `rglob("*")` and using `@lru_cache` provides massive performance gains, especially for frequently accessed API endpoints like shuffles or previews.
**Action:** Always look for opportunities to combine directory scans and cache the results of expensive I/O operations in Flask applications.

## 2025-05-14 - [Import Overhead]
**Learning:** Importing libraries like `subprocess` or `random` inside function scopes adds unnecessary overhead if those functions are called frequently (e.g., in a web API).
**Action:** Move common library imports to the top level of the module to optimize execution speed.
