# Hi, We Are HueSurf

<p align="center">
  <img src="assets/huesurf.png" alt="HueSurf Logo" width="340" style="vertical-align:middle;"/>
  <img src="assets/huesurfmacos.png" alt="HueSurf macOS Logo" width="340" style="vertical-align:middle; margin-left:16px;"/>
</p>

##  What is HueSurf?

HueSurf is a design focused, minimalist, fast, and privacy-focused browser built on Chromium. We stripped out the annoying ads, sponsored junk, telemtry, bloat, and AI slop. This project is crafted by a trio of Middle School devs, with the purpose of making web surfing clean and simple.

## Features

-  **No Ads, No Sponsors** – Surf the web distraction-free.
-  **No AI** – Your data stays yours, no weird robots lurking.
-  **Lightweight** – Minimal footprint, quick to start, easy on your systems RAM.
-  **Open Source** – Fork it and modify it however you like.
-  **Lightweight** – Minimal footprint, quick to start, and easy on your systems RAM.
-  **Open Source** – Fork it and make it your own. (Please dont unless you want to contribute to us, that would be great!)
-  **No Google** - Hey/OK Google! Delete yourself from our browser!

##  Installation

> **Note:** HueSurf is in development. Some features may change! Some might stay, I hope it's stay beacause I *DONT* want wasted potential! 
> No releases are ready yet. (sorry people with weaker PC's)

## Building from Source

HueSurf uses a **patch-based build system** that downloads Chromium source and applies HueSurf modifications (patches) during build time. This keeps our repository lightweight (it's only large beacause of assets) while enabling full customization. so uhhh press play and give up your computer.

**Quick Start:**
```bash
# Clone the repository
git clone https://github.com/H3-Apps/HueSurf.git
cd HueSurf

# Make build script executable
chmod +x scripts/build.sh

# Start the build(This takes a while! 5 hours just to download on a 2019 16 inch i7 macbook pro!)
./scripts/build.sh
```

**Requirements:**
- 16GB+ RAM (24GB recommended)
- 110GB free disk space (as of now)
- Multi-core CPU (4+ cores recommended)
- 1-4 hours build time (depending on hardware)

**Supported Platforms:**

-  Linux (Ubuntu 18.04+, Debian 10+, CentOS 8+)
-  Temple OS
-  MacOS (10.15+ Catalina or later BUT PLEASE PLEASE use ventura or newer.)
-  Windows (10/11 with Visual Studio 2019+)
-  Pebble OS 
For detailed build instructions, see [BUILD.md](BUILD.md).

##  Project Structure

```
HueSurf/
├── scripts/build.sh           # Main build orchestrator
├── patches/                   # HueSurf patches/mods to Chromium
├── config/                    # Build configuration files
├── website/                   # HueSurf website and hosting
├── BUILD.md                   # Comprehensive build guide
└── dist/                      # Built browser packages (created during build)
```

##  Contributing

We welcome any PRs or ideas that you may have. Fork the code and open a pull request or share some ideas in the disscusions.

##  License

This project is licensed under the MIT license.

## Star History

<a href="https://www.star-history.com/#H3-Apps/HueSurf&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=H3-Apps/HueSurf&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=H3-Apps/HueSurf&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=H3-Apps/HueSurf&type=Date" />
 </picture>
</a>

## Support & Donations

We’re open to donations! If you want to support HueSurf feel free to donate.
---

**Made with 💚 by 3 dudes (H3, vexalous, and i love pand ass).**
