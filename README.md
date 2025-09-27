<!-- DONT MODIFY THIS FILE -->
# HueSurf

> A lightweight Chromium-based browser without any ADs, AI, Sponsors, or bloat.  
> Created by 3 dudes, we want this to be small but we are open to donations!!!

---

##  What is HueSurf?

HueSurf is a minimal, fast, and privacy-focused browser built on Chromium. We stripped out the annoying ads, sponsored junk, telemtry, bloat, and all that AI nonsense. This project is crafted by a trio of chill devs, with the plan of making web surfing clean and simple.

## Features

-  **No Ads, No Sponsors** – Surf the web distraction-free.
-  **No AI** – Your data stays yours, no weird bots lurking.
-  **Lightweight** – Minimal footprint, quick to start, easy on your systems RAM.
-  **Open Source** – Fork it and modify it however you like.
-  **Lightweight** – Minimal footprint, quick to start, and easy on your systems RAM.
-  **Open Source** – Fork it and make it your own.

##  Installation

> **Note:** HueSurf is in active development. Some features may change!  
> No releases are ready yet.

### Building from Source

HueSurf uses a **patch-based build system** that downloads Chromium source and applies HueSurf modifications during build time. This keeps our repository lightweight while enabling full customization.

**Quick Start:**
```bash
# Clone the repository
git clone https://github.com/H3-Apps/HueSurf.git
cd HueSurf

# Make build script executable
chmod +x scripts/build.sh

# Start the build (This takes a while!)
./scripts/build.sh
```

**Requirements:**
- 8GB+ RAM (16GB recommended)
- 50GB free disk space  
- Multi-core CPU (4+ cores recommended)
- 1-4 hours build time (depending on hardware)

**Supported Platforms:**
-  Linux (Ubuntu 18.04+, Debian 10+, CentOS 8+)
-  macOS (10.15+ Catalina or later)
-  Windows (10/11 with Visual Studio 2019+)

For detailed build instructions, see [BUILD.md](BUILD.md).

##  Project Structure

```
HueSurf/
├── scripts/build.sh           # Main build orchestrator
├── patches/                   # HueSurf modifications to Chromium
├── config/                    # Build configuration files
├── website/                   # Official HueSurf website
├── BUILD.md                   # Comprehensive build guide
└── dist/                      # Built browser packages (created during build)
```

##  Contributing

We welcome any PRs or ideas that you may have. Fork the code and open a pull request or share some ideas in the disscusions.

##  License

This project is licensed under the MIT license.

## 💸 Support & Donations

We’re open to donations! If you want to support HueSurf feel free to donate.
---

**Made with 💚 by 3 dudes (H3, vexalous, and i love pand ass).**
