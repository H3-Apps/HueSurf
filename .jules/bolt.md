# Bolt's Performance Journal

## 2025-05-15 - [Consolidating Filesystem Scans]
**Learning:** Repetitive `glob` and `rglob` calls on the same directory are a significant source of I/O overhead in Flask apps. Consolidating these into a single pass using a cached helper function significantly reduces response times, even for small datasets.

**Action:** Always look for redundant filesystem traversals and use `@lru_cache` with immutable return types (like tuples) to store results.

## 2025-05-15 - [Securing State-Changing Endpoints]
**Learning:** Endpoints that trigger expensive or state-changing operations (like repacking assets) should always be restricted to `POST` to prevent CSRF and unintended triggers from search crawlers or browser pre-fetching.

**Action:** Ensure all non-idempotent API routes use `methods=["POST"]`.
