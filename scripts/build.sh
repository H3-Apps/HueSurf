#!/bin/bash
# HueSurf Build Script - Ubuntu + macOS Support

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLATFORM="$(uname | tr '[:upper:]' '[:lower:]')"
CHROMIUM_VERSION="131.0.6778.85"
OUT_DIR="$PROJECT_ROOT/chromium_src/src/out/HueSurf"
JOBS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

echo "🌊🏄‍♂️ HueSurf Build Script"
echo "========================"
echo "Platform: $PLATFORM"
echo "Chromium Version: $CHROMIUM_VERSION"
echo "Project Root: $PROJECT_ROOT"
echo

# --------------------------
# Install system dependencies
# --------------------------
install_dependencies() {
    echo "[HueSurf] Checking system dependencies..."

    if [[ "$PLATFORM" == "linux" ]]; then
        if command -v apt-get &>/dev/null; then
            sudo apt-get update
            sudo apt-get install -y \
                build-essential gperf ninja-build pkg-config \
                python3 python3-dev python3-pip python3-venv \
                clang lld llvm \
                libgtk-3-dev libnss3-dev libasound2-dev libxss-dev \
                libxrandr-dev libxtst-dev libxkbfile-dev libxcomposite-dev \
                libxdamage-dev libxfixes-dev libxext-dev libx11-dev \
                libexpat1-dev libdbus-1-dev curl git
        else
            echo "[ERROR] Unknown Linux distribution. Please install build deps manually."
            exit 1
        fi
    elif [[ "$PLATFORM" == "darwin" ]]; then
        if ! command -v brew &>/dev/null; then
            echo "[HueSurf] Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        echo "[HueSurf] Installing dependencies via Homebrew..."
        brew install python ninja gperf pkg-config git clang lld llvm
    else
        echo "[ERROR] Unsupported platform: $PLATFORM"
        exit 1
    fi

    echo "[HueSurf] ✅ Dependencies installed"
}

# --------------------------
# Install depot_tools
# --------------------------
install_depot_tools() {
    DEPOT_DIR="$PROJECT_ROOT/depot_tools"
    if [[ ! -d "$DEPOT_DIR" ]]; then
        echo "[HueSurf] Installing depot_tools..."
        git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git "$DEPOT_DIR"
    else
        echo "[HueSurf] depot_tools already exists, updating..."
        (cd "$DEPOT_DIR" && git pull)
    fi

    export PATH="$DEPOT_DIR:$PATH"
    echo "[HueSurf] ✅ depot_tools ready"
}

# --------------------------
# Fetch Chromium source
# --------------------------
fetch_chromium() {
    SRC_DIR="$PROJECT_ROOT/chromium_src/src"
    if [[ ! -d "$SRC_DIR" ]]; then
        echo "[HueSurf] Fetching Chromium source (this may take a while)..."
        mkdir -p "$PROJECT_ROOT/chromium_src"
        cd "$PROJECT_ROOT/chromium_src"
        fetch --nohooks chromium
    else
        echo "[HueSurf] Chromium source already present, updating..."
        cd "$SRC_DIR"
        git pull
        gclient sync
    fi
}

# --------------------------
# Configure build
# --------------------------
configure_build() {
    echo "[HueSurf] Configuring GN build..."
    cd "$PROJECT_ROOT/chromium_src/src"

    mkdir -p "$OUT_DIR"

    if [[ "$PLATFORM" == "linux" ]]; then
        GN_ARGS="is_debug=false is_component_build=false enable_nacl=false use_ozone=true ozone_platform=\"x11\""
    elif [[ "$PLATFORM" == "darwin" ]]; then
        GN_ARGS="is_debug=false is_component_build=false enable_nacl=false mac_deployment_target=\"10.15\""
    else
        echo "[ERROR] Unsupported platform for GN config"
        exit 1
    fi

    gn gen "$OUT_DIR" --args="$GN_ARGS"
}

# --------------------------
# Build Chromium (HueSurf)
# --------------------------
build_browser() {
    echo "[HueSurf] Starting build..."
    cd "$PROJECT_ROOT/chromium_src/src"
    ninja -C "$OUT_DIR" chrome -j"$JOBS"
    echo "[HueSurf] ✅ Build completed successfully"
}

# --------------------------
# Run HueSurf (Chromium)
# --------------------------
run_browser() {
    echo "[HueSurf] Running HueSurf..."
    if [[ "$PLATFORM" == "darwin" ]]; then
        "$OUT_DIR/Chromium.app/Contents/MacOS/Chromium" --user-data-dir="$PROJECT_ROOT/huesurf_profile"
    else
        "$OUT_DIR/chrome" --user-data-dir="$PROJECT_ROOT/huesurf_profile"
    fi
}

# --------------------------
# Main
# --------------------------
case "$1" in
    run)
        run_browser
        ;;
    *)
        install_dependencies
        install_depot_tools
        fetch_chromium
        configure_build
        build_browser
        ;;
esac
