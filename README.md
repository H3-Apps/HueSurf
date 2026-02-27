# HueSurf

![HueSurf Logo](assets/huesurf.png) ![HueSurf macOS Logo](assets/huesurfmacos.png)

## What is HueSurf?

HueSurf is a design-focused, minimalist, fast, and privacy-focused browser built on Chromium. We stripped out the annoying ads, sponsored junk, telemetry, bloat, and AI slop. This project is crafted by a trio of middle school devs with the purpose of making web surfing clean and simple.

## Features

1. **No Ads, No Sponsors** – Surf the web distraction-free.
2. **No AI** – Your data stays yours; no weird robots lurking.
3. **Lightweight** – Minimal footprint, quick to start, and easy on your system's RAM.
4. **Open Source** – Fork it and modify it however you like.
5. **No Google** – Hey/OK Google! Delete yourself from our browser!

## Installation

> **Note:** HueSurf is in development. Some features may change! I hope they stay because I *don't* want wasted potential!
> No releases are ready yet. (Sorry, people with weaker PCs!)

## Building from Source

HueSurf uses a patch-based build system that downloads Chromium source and applies HueSurf modifications (patches) during build time. This helps keep our repository lightweight (it's only large because of assets) while still enabling full customization. So, press play and prepare your computer for a workout.

### Quick Start

```bash
# Clone the repository.
git clone https://github.com/H3-Apps/HueSurf.git
cd HueSurf

# Make the build script executable.
chmod +x scripts/build.sh

# Start the build.
./scripts/build.sh
```

### Requirements

1. **16 GB+ RAM** (24 GB recommended)
2. **110 GB free disk space** (as of now)
3. **Multi-core CPU** (4+ cores recommended)
4. **Average build time:** 1–4 hours (faster or slower depending on hardware)

### Supported Platforms

1. **Linux** (Ubuntu 18.04+, Debian 10+, CentOS 8+)
2. **Temple OS**
3. **macOS** (10.15 "Catalina" or later; Ventura or newer highly recommended)
4. **Windows 10/11** (with Visual Studio 2019+)
5. **Pebble OS**

For detailed build instructions, see [BUILD.md](BUILD.md).

## Project Structure

```
HueSurf/
├── scripts/build.sh           # Main build orchestrator
├── patches/                   # HueSurf patches/mods to Chromium
├── config/                    # Build configuration files
├── website/                   # HueSurf website and hosting
├── BUILD.md                   # Comprehensive build guide
└── dist/                      # Built browser packages (created during build)
```

## Contributing

We welcome any PRs or ideas that you may have. Fork the code and open a pull request or share some ideas in the discussions.

## License

This project is licensed under the MIT license.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=H3-Apps/HueSurf&type=Date)](https://star-history.com/#H3-Apps/HueSurf&Date)

## Support & Donations

We’re open to donations! If you want to support HueSurf, feel free to donate.

Made with 💚 by 3 dudes (H3, vexalous, and i love pandass).
