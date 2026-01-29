## 2024-10-25 - Efficient Directory Scanning
**Learning:** `os.scandir` is significantly faster (~3x speedup) than multiple `glob` calls for finding files with specific extensions. It performs a single system call to iterate directory entries and provides access to file attributes without extra stat calls.
**Action:** Optimized `get_wallpaper_preview` by replacing 4 sequential `glob` scans with a single `os.scandir` loop, using a priority logic map to preserve the precedence of `.png` > `.jpg` > `.jpeg` > `.webp`.
