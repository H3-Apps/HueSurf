# Building HueSurf from Source

> A comprehensive guide to building HueSurf - the lightweight Chromium browser without ads, AI, sponsors, or bloat.

Made by 3 dudes who got tired of bloated browsers (and potentially a robot if Javier goes insane! 😜).

## 🌊 Overview

HueSurf uses a **patch-based build system** similar to other successful Chromium forks like Ungoogled Chromium and Brave. This approach:

- ✅ **Keeps our repo lightweight** (no massive Chromium source in Git)
- ✅ **Makes updates manageable** (just update patches)
- ✅ **Enables easy customization** (modify patches for your needs)
- ✅ **Follows best practices** used by major Chromium forks

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/H3-Apps/HueSurf.git
cd HueSurf

# Make build script executable
chmod +x scripts/build.sh

# Start the build (grab some coffee, this takes a while!)
./scripts/build.sh
```

That's it! The script handles everything: downloading Chromium source, applying HueSurf patches, and building the browser.

## 📋 System Requirements

### Minimum Requirements

- **RAM**: 8GB (16GB+ recommended)
- **Disk Space**: 50GB free space
- **CPU**: Multi-core processor (4+ cores recommended)
- **Time**: 1-4 hours for full build (depends on hardware)

### Operating System Support

| OS | Status | Notes |
|----|--------|-------|
| 🐧 **Linux** | ✅ Fully Supported | Ubuntu 18.04+, Debian 10+, CentOS 8+ |
| 🍎 **macOS** | ✅ Fully Supported | macOS 10.15+ (Catalina or later) |
| 🪟 **Windows** | ⚠️ Experimental | Windows 10/11 with VS 2019+ |

## 🛠️ Build Process Explained

### 1. **Source Management**
```
HueSurf/
├── scripts/build.sh        # Main build orchestrator
├── patches/               # HueSurf-specific modifications
├── config/               # Build configuration files
├── chromium_src/         # Chromium source (downloaded during build)
└── dist/                # Final browser packages
```

### 2. **Build Steps**

The build process follows these stages:

1. **📥 Fetch Chromium Source** - Downloads official Chromium source code
2. **🩹 Apply Patches** - Applies HueSurf modifications (ad blocking, privacy, branding)  
3. **⚙️ Configure Build** - Generates optimized build configuration
4. **🔨 Compile Browser** - Builds the actual browser binary
5. **📦 Package Release** - Creates distributable packages

## 🔧 Platform-Specific Setup

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install -y \
    git python3 python3-pip \
    build-essential \
    curl wget \
    lsb-release \
    sudo

# Additional packages for Chromium build
sudo apt install -y \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libcups2-dev \
    libgtk-3-dev \
    libgconf-2-4

# Clone and build
git clone https://github.com/H3-Apps/HueSurf.git
cd HueSurf
./scripts/build.sh
```

### macOS

```bash
# Install Xcode command line tools
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install git python3

# Clone and build
git clone https://github.com/H3-Apps/HueSurf.git
cd HueSurf
./scripts/build.sh
```

### Windows

```powershell
# Install Visual Studio 2019 or later with C++ workload
# Install Git for Windows
# Install Python 3.7+

# Clone repository
git clone https://github.com/H3-Apps/HueSurf.git
cd HueSurf

# Run build (use Git Bash or PowerShell)
bash scripts/build.sh
```

## ⚡ Build Script Usage

The `scripts/build.sh` script supports different commands:

```bash
# Full build (default)
./scripts/build.sh

# Individual steps
./scripts/build.sh deps     # Install dependencies only
./scripts/build.sh fetch    # Download Chromium source only
./scripts/build.sh patch    # Apply patches only
./scripts/build.sh build    # Compile only
./scripts/build.sh package  # Package only
./scripts/build.sh clean    # Clean build directory

# Get help
./scripts/build.sh help
```

## 🩹 Understanding Patches

HueSurf modifications are organized as patch files in the `patches/` directory:

```
patches/
├── 001-huesurf-branding.patch      # Replace Chromium branding with HueSurf
├── 002-remove-google-services.patch # Remove Google integrations
├── 003-privacy-enhancements.patch   # Enhanced privacy settings
├── 004-ad-blocking.patch           # Built-in ad blocking
├── 005-ui-cleanup.patch            # Remove promotional UI elements
└── 006-performance-tweaks.patch    # Performance optimizations
```

### Creating New Patches

1. **Make changes** in `chromium_src/src/`
2. **Generate patch**:
   ```bash
   cd chromium_src/src
   git diff > ../../patches/007-my-feature.patch
   ```
3. **Test patch**:
   ```bash
   ./scripts/build.sh patch
   ```

## 🎛️ Build Configuration

### Custom Build Arguments

Modify `config/custom_args.gn` to customize your build:

```gn
# Example: Enable debug build
is_debug = true

# Example: Disable specific features
enable_widevine = false
enable_nacl = false

# Example: Add custom branding
huesurf_custom_name = "MyBrowser"
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROMIUM_VERSION` | Chromium version to build | `120.0.6099.199` |
| `JOBS` | Parallel build jobs | Auto-detected |
| `HUESURF_BRANDING` | Enable HueSurf branding | `true` |

## 🚨 Troubleshooting

### Common Issues

**❌ "depot_tools not found"**
```bash
# Solution: Re-run dependency installation
./scripts/build.sh deps
```

**❌ "Out of disk space during build"**
```bash
# Solution: Free up space and clean build
./scripts/build.sh clean
./scripts/build.sh
```

**❌ "Build failed with compilation errors"**
```bash
# Solution: Check specific platform requirements
# Linux: Install missing dev packages
sudo apt install libnss3-dev libgconf-2-4

# macOS: Update Xcode
xcode-select --install

# Windows: Install Visual Studio C++ workload
```

**❌ "Patches fail to apply"**
```bash
# Solution: Chromium version mismatch
# Check patches/README.md for compatible versions
# or update patches for newer Chromium
```

### Debug Build

For development, use debug builds:

```bash
# Edit config/custom_args.gn
echo "is_debug = true" >> config/custom_args.gn

# Rebuild
./scripts/build.sh clean
./scripts/build.sh
```

### Build Logs

Build logs are saved to:
- Linux/macOS: `chromium_src/src/out/HueSurf/build.log`
- Windows: `chromium_src\src\out\HueSurf\build.log`

## 🔄 Development Workflow

### Making Changes

1. **Edit source code** in `chromium_src/src/`
2. **Test changes**:
   ```bash
   ./scripts/build.sh build  # Quick rebuild
   ```
3. **Create patch**:
   ```bash
   cd chromium_src/src
   git diff > ../../patches/new-feature.patch
   ```
4. **Full test**:
   ```bash
   ./scripts/build.sh clean
   ./scripts/build.sh
   ```

### Updating Chromium Version

1. **Update version** in `scripts/build.sh`:
   ```bash
   CHROMIUM_VERSION="121.0.6167.85"  # New version
   ```
2. **Clean and rebuild**:
   ```bash
   ./scripts/build.sh clean
   ./scripts/build.sh
   ```
3. **Fix any patch conflicts** that arise

## 📦 Distribution

Built browsers are packaged in `dist/`:

```
dist/
├── huesurf-120.0.6099.199-linux/    # Linux build
├── huesurf-120.0.6099.199-mac/      # macOS build
└── huesurf-120.0.6099.199-windows/  # Windows build
```

### Creating Releases

```bash
# Build for all platforms (if supported)
./scripts/build.sh

# Package will be in dist/
ls -la dist/
```

## 🤝 Contributing

### Patch Guidelines

1. **One feature per patch** - Keep patches focused
2. **Descriptive names** - `feature-description.patch`
3. **Test thoroughly** - Ensure builds work on all platforms
4. **Document changes** - Update relevant documentation

### Pull Requests

When submitting patches:

1. **Test on multiple platforms** (if possible)
2. **Include build instructions** for new features
3. **Update documentation** if needed
4. **Follow our philosophy**: No ads, no AI, no bloat!

## 📚 Resources

### Useful Links

- **Chromium Build Instructions**: https://chromium.googlesource.com/chromium/src/+/main/docs/linux/build_instructions.md
- **GN Build Reference**: https://gn.googlesource.com/gn/+/main/docs/reference.md
- **Depot Tools**: https://commondatastorage.googleapis.com/chrome-infra-docs/flat/depot_tools/docs/html/depot_tools_tutorial.html

### Similar Projects

- **Ungoogled Chromium**: https://github.com/Eloston/ungoogled-chromium
- **Brave Browser**: https://github.com/brave/brave-browser
- **Iridium Browser**: https://iridiumbrowser.de/

## 🏆 Build Success!

When your build completes successfully, you'll see:

```
🎉 HueSurf build completed! No ads, no AI, no bloat, no problem!
📦 Binary location: /path/to/HueSurf/dist/huesurf-VERSION-PLATFORM/
```

Launch your freshly built HueSurf browser and enjoy distraction-free browsing!

---

## 💚 Support

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join the community conversation
- **Donations**: Support the 3 dudes keeping this project alive!

Remember: If Javier starts adding robots to the build process, please contact us immediately. We will spank him so hard his butt will explode of being hurt so hard. 🤖

---

Made with 💚 by 3 dudes who believe the web should be clean, fast, and simple.