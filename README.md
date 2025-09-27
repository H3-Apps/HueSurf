# HueSurf

> A lightweight Chromium-based browser without any ADs, AI, Sponsors, or bloat.  
> Created by 3 dudes, we want this to be small but we are open to donations!!!

---

## 🚀 What is HueSurf?

HueSurf is a minimal, fast, and privacy-focused browser built on Chromium. We stripped out the annoying ads, sponsored junk, telemetry, bloat, and all that AI nonsense. This project is crafted by a trio of chill devs, with the plan of making web surfing clean and simple.

## ✨ Features

- 🧹 **No Ads, No Sponsors** – Surf the web distraction-free.
- 🤖 **No AI** – Your data stays yours, no weird bots lurking.
- 🪶 **Lightweight** – Minimal footprint, quick to start, easy on your systems RAM.
- 🛠️ **Open Source** – Fork it, star it, and make it your own.
- 💸 **Donation Friendly** – If you vibe with us, show some love!

## 💸 Support & Donations

We’re open to donations! If you want to help us keep HueSurf alive and bloat-free, hit the donate button or reach out!

## 🛠️ Installation

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

# Start the build (grab some coffee, this takes a while!)
./scripts/build.sh
```

**Requirements:**
- 8GB+ RAM (16GB recommended)
- 50GB free disk space  
- Multi-core CPU (4+ cores recommended)
- 1-4 hours build time (depending on hardware)

**Supported Platforms:**
- 🐧 Linux (Ubuntu 18.04+, Debian 10+, CentOS 8+)
- 🍎 macOS (10.15+ Catalina or later)
- 🪟 Windows (10/11 with Visual Studio 2019+)

For detailed build instructions, see [BUILD.md](BUILD.md).

## 💾 Project Structure

```
HueSurf/
├── scripts/build.sh           # Main build orchestrator
├── patches/                   # HueSurf modifications to Chromium
├── config/                    # Build configuration files
├── website/                   # Official HueSurf website
├── BUILD.md                   # Comprehensive build guide
└── dist/                     # Built browser packages (created during build)
```

Our **patch-based approach** means:
- ✅ **Lightweight repo** - No massive Chromium source in Git
- ✅ **Easy updates** - Just update patches for new Chromium versions  
- ✅ **Full transparency** - Every change is visible in patch files
- ✅ **Community friendly** - Easy to review and contribute to modifications

## 🤝 Contributing

We welcome PRs, ideas, and memes (no labubu syscall 🥲). Fork, code, open a pull request, or just vibe in the discussions.

**Ways to contribute:**
- 🐛 **Report bugs** - Found an issue? Let us know!
- 🩹 **Create patches** - Add features or fix problems
- 📖 **Improve docs** - Help others understand the project
- 💰 **Donate** - Support the 3 dudes keeping this alive

If Javier starts adding robots, DM us ASAP. We will spank him so hard his butt will explode of being hurt so hard.

## 📜 License

MIT. Do what you want, just don't add ads. Or sell it with little to no difference.

---

**Made with 💚 by 3 dudes (H3, vexalous, and i love pand ass) and potentially a robot if Javier goes insane! 😜**
