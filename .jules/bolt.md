## 2024-05-22 - N+1 Directory Scanning
**Learning:** Using multiple `glob` calls combined with `rglob` on the same directory results in redundant filesystem scans (N+1 scans), which scales poorly with directory size.
**Action:** Replace multiple `glob` calls with a single `os.walk` or `os.scandir` traversal to perform counting and sizing in one pass.
