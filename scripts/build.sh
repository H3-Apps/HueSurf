#!/bin/bash

# HueSurf Build Script
# Builds HueSurf browser from Chromium source with HueSurf modifications
# Made by 3 dudes who got tired of bloated browsers

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHROMIUM_VERSION="131.0.6778.85"  # Updated to latest stable version for macOS 26 compatibility
BUILD_DIR="$PROJECT_ROOT/chromium_src"
DEPOT_TOOLS_DIR="$PROJECT_ROOT/depot_tools"
PATCHES_DIR="$PROJECT_ROOT/patches"
CONFIG_DIR="$PROJECT_ROOT/config"

# Platform detection
PLATFORM=""
case "$(uname -s)" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="mac";;
    CYGWIN*|MINGW*|MSYS*) PLATFORM="windows";;
    *)          echo -e "${RED}❌ Unsupported platform$(uname -s)${NC}" && exit 1;;
esac

echo -e "${BLUE}🌊🏄‍♂️ HueSurf Build Script${NC}"
echo -e "${BLUE}========================${NC}"
echo -e "Platform: ${GREEN}$PLATFORM${NC}"
echo -e "Chromium Version: ${GREEN}$CHROMIUM_VERSION${NC}"
echo -e "Project Root: ${GREEN}$PROJECT_ROOT${NC}"
echo ""

# Function to print status messages
log() {
    echo -e "${GREEN}[HueSurf]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Ensure depot_tools is in PATH
ensure_depot_tools_path() {
    export PATH="$DEPOT_TOOLS_DIR:$PATH"
}

# Install depot_tools
install_depot_tools() {
    log "Installing depot_tools..."

    if [ -d "$DEPOT_TOOLS_DIR" ]; then
        log "depot_tools already exists, updating..."
        cd "$DEPOT_TOOLS_DIR"
        git pull origin main
    else
        log "Cloning depot_tools..."
        git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git "$DEPOT_TOOLS_DIR"
    fi

    # Add to PATH for this session
    export PATH="$DEPOT_TOOLS_DIR:$PATH"

    # Verify installation
    if command_exists gclient; then
        log "✅ depot_tools installed successfully"
    else
        error "Failed to install depot_tools"
    fi
}

# Monitor progress of long-running operations
monitor_progress() {
    local pid=$1
    local desc=$2
    local dot_count=0

    echo -ne "${GREEN}[HueSurf]${NC} $desc"

    while kill -0 $pid 2>/dev/null; do
        echo -ne "."
        dot_count=$((dot_count + 1))
        if [ $dot_count -eq 50 ]; then
            echo ""
            echo -ne "${GREEN}[HueSurf]${NC} Still working on $desc"
            dot_count=0
        fi
        sleep 2
    done
    echo ""
}

# Download Chromium source
fetch_chromium() {
    log "Fetching Chromium source code..."

    ensure_depot_tools_path
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"

    if [ ! -d "src" ]; then
        log "Initializing Chromium checkout (this will take a while...)"
        log "💡 This downloads the initial Chromium source (~2GB)"
        fetch --nohooks chromium
    fi

    cd src

    log "Checking out Chromium version $CHROMIUM_VERSION..."
    git checkout "refs/tags/$CHROMIUM_VERSION" -b huesurf-build

    log "Running gclient sync (this may take 30+ minutes, downloading ~10GB)..."
    log "💡 Tip: You can monitor progress by checking disk usage with: du -sh chromium_src/"

    # Run gclient sync with progress monitoring
    gclient sync --with_branch_heads --with_tags --jobs 1 --verbose --jobs=4 &
    SYNC_PID=$!

    # Monitor the sync process
    monitor_progress $SYNC_PID "Syncing Chromium source"

    # Wait for the process to complete and check exit status
    wait $SYNC_PID
    SYNC_EXIT_CODE=$?

    if [ $SYNC_EXIT_CODE -ne 0 ]; then
        error "gclient sync failed with exit code $SYNC_EXIT_CODE"
    fi

    log "✅ Chromium source fetched successfully"
}

# Apply HueSurf patches
apply_patches() {
    log "Applying HueSurf patches..."

    cd "$BUILD_DIR/src"

    # Check if patches directory exists and has patches
    if [ ! -d "$PATCHES_DIR" ] || [ -z "$(find "$PATCHES_DIR" -name "*.patch" 2>/dev/null)" ]; then
        warn "No patches found in $PATCHES_DIR - skipping patch application"
        return 0
    fi

    # Apply patches in order
    for patch in "$PATCHES_DIR"/*.patch; do
        if [ -f "$patch" ]; then
            log "Applying patch: $(basename "$patch")"
            if ! git apply --check "$patch" 2>/dev/null; then
                warn "Patch $(basename "$patch") cannot be applied cleanly - skipping"
                continue
            fi
            git apply "$patch" || warn "Failed to apply patch: $(basename "$patch")"
        fi
    done

    log "✅ Patches applied"
}

# Generate build configuration
generate_build_config() {
    log "Generating build configuration..."

    cd "$BUILD_DIR/src"

    # Create args.gn file
    BUILD_ARGS_FILE="out/HueSurf/args.gn"
    mkdir -p "$(dirname "$BUILD_ARGS_FILE")"

    cat > "$BUILD_ARGS_FILE" << EOF
# HueSurf Build Configuration
# Generated by HueSurf build script

# Basic build settings
is_debug = false
symbol_level = 1
is_official_build = true
is_component_build = false

# HueSurf branding and features
chrome_pgo_phase = 0
enable_nacl = false
enable_widevine = false

# Privacy and bloat removal
enable_reporting = false
enable_background_mode = false
enable_google_now = false
enable_hotwording = false
enable_webrtc = true
enable_hangout_services_extension = false
enable_mdns = false
enable_service_discovery = false
enable_wifi_bootstrapping = false
enable_supervised_users = false
safe_browsing_mode = 0
enable_extensions = true
enable_plugins = true

# Performance optimizations
use_jumbo_build = true
use_thin_lto = true
chrome_pgo_phase = 0

# Platform-specific settings
EOF

    # Add platform-specific configurations
    case "$PLATFORM" in
        "linux")
            cat >> "$BUILD_ARGS_FILE" << EOF

# Linux specific
use_sysroot = true
use_custom_libcxx = false
treat_warnings_as_errors = false
use_ozone = true
ozone_auto_platforms = false
ozone_platform = "x11"
ozone_platform_x11 = true
ozone_platform_wayland = true
EOF
            ;;
        "mac")
            cat >> "$BUILD_ARGS_FILE" << EOF

# macOS specific
mac_deployment_target = "10.15.0"
treat_warnings_as_errors = false
EOF
            ;;
        "windows")
            cat >> "$BUILD_ARGS_FILE" << EOF

# Windows specific
is_win_fastlink = false
treat_warnings_as_errors = false
EOF
            ;;
    esac

    # Copy custom config if it exists
    if [ -f "$CONFIG_DIR/custom_args.gn" ]; then
        log "Appending custom build arguments..."
        echo "" >> "$BUILD_ARGS_FILE"
        echo "# Custom HueSurf arguments" >> "$BUILD_ARGS_FILE"
        cat "$CONFIG_DIR/custom_args.gn" >> "$BUILD_ARGS_FILE"
    fi

    log "✅ Build configuration generated"
}

# Build HueSurf
build_browser() {
    log "Building HueSurf browser..."

    ensure_depot_tools_path
    cd "$BUILD_DIR/src"

    # Generate build files
    log "Generating build files with gn..."
    gn gen out/HueSurf --args="$(cat out/HueSurf/args.gn | tr '\n' ' ')"

    # Determine number of parallel jobs
    JOBS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "4")
    log "Building with $JOBS parallel jobs..."

    # Build the browser
    ninja -C out/HueSurf chrome -j"$JOBS"

    log "✅ HueSurf built successfully!"
    log "📦 Binary location: $BUILD_DIR/src/out/HueSurf/"
}

# Package the build
package_build() {
    log "Packaging HueSurf..."

    cd "$BUILD_DIR/src/out/HueSurf"

    # Create package directory
    PACKAGE_DIR="$PROJECT_ROOT/dist/huesurf-$CHROMIUM_VERSION-$PLATFORM"
    mkdir -p "$PACKAGE_DIR"

    case "$PLATFORM" in
        "linux")
            cp -r chrome chrome_sandbox locales resources *.pak *.so "$PACKAGE_DIR/" 2>/dev/null || true
            ;;
        "mac")
            cp -r Chromium.app "$PACKAGE_DIR/" 2>/dev/null || true
            # Rename app bundle
            if [ -d "$PACKAGE_DIR/Chromium.app" ]; then
                mv "$PACKAGE_DIR/Chromium.app" "$PACKAGE_DIR/HueSurf.app"
            fi
            ;;
        "windows")
            cp -r chrome.exe chrome_sandbox.exe locales resources *.pak *.dll "$PACKAGE_DIR/" 2>/dev/null || true
            ;;
    esac

    log "✅ Package created: $PACKAGE_DIR"
}

# Check system dependencies
check_dependencies() {
    log "Checking system dependencies..."

    # Required tools
    REQUIRED_TOOLS=("git" "python3")

    for tool in "${REQUIRED_TOOLS[@]}"; do
        if ! command_exists "$tool"; then
            error "Required tool not found: $tool"
        fi
    done

    # Platform-specific dependencies
    case "$PLATFORM" in
        "linux")
            # Check for common build dependencies
            if ! dpkg -l | grep -q build-essential 2>/dev/null && ! rpm -qa | grep -q gcc 2>/dev/null; then
                warn "Build tools may not be installed. Install build-essential (Ubuntu/Debian) or gcc (CentOS/RHEL)"
            fi
            ;;
        "mac")
            if ! xcode-select -p >/dev/null 2>&1; then
                error "Xcode command line tools not installed. Run: xcode-select --install"
            fi
            ;;
        "windows")
            warn "Windows build requires Visual Studio 2019 or later"
            ;;
    esac

    log "✅ Dependencies check completed"
}

# Clean build directory
clean() {
    log "Cleaning build directory..."
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        log "✅ Build directory cleaned"
    else
        log "Build directory already clean"
    fi
}

# Show usage information
usage() {
    echo "HueSurf Build Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  all        - Complete build process (default)"
    echo "  deps       - Install depot_tools and check dependencies"
    echo "  fetch      - Download Chromium source code"
    echo "  patch      - Apply HueSurf patches"
    echo "  config     - Generate build configuration"
    echo "  build      - Build the browser"
    echo "  package    - Package the built browser"
    echo "  clean      - Clean build directory"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Full build"
    echo "  $0 clean     # Clean and start fresh"
    echo "  $0 build     # Just build (if source already fetched)"
    echo ""
}

# Main build process
main() {
    local command="${1:-all}"

    case "$command" in
        "all")
            check_dependencies
            install_depot_tools
            fetch_chromium
            apply_patches
            generate_build_config
            build_browser
            package_build
            log "🎉 HueSurf build completed! No ads, no AI, no bloat, no problem!"
            ;;
        "deps")
            check_dependencies
            install_depot_tools
            ;;
        "fetch")
            install_depot_tools
            fetch_chromium
            ;;
        "patch")
            apply_patches
            ;;
        "config")
            generate_build_config
            ;;
        "build")
            build_browser
            ;;
        "package")
            package_build
            ;;
        "clean")
            clean
            ;;
        "help")
            usage
            ;;
        *)
            error "Unknown command: $command. Use '$0 help' for usage information."
            ;;
    esac
}

# Trap to clean up on script exit
trap 'echo -e "\n${YELLOW}Build interrupted${NC}"' INT TERM

# Run main function with all arguments
main "$@"
