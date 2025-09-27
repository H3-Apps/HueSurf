#!/bin/bash

# HueSurf Wallpaper Packer Script
# Easy-to-use wrapper for pack_wallpapers.py

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PACKER_SCRIPT="$SCRIPT_DIR/pack_wallpapers.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements_packer.txt"

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}"
    echo "🎨 ======================================="
    echo "   HueSurf Wallpaper Packer"
    echo "   Pack wallpapers for web distribution"
    echo "=======================================${NC}"
    echo
}

# Check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        print_info "Please install Python 3.7+ and try again"
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_info "Using Python $PYTHON_VERSION ($PYTHON_CMD)"
}

# Check if dependencies are installed
check_dependencies() {
    print_info "Checking dependencies..."

    if $PYTHON_CMD -c "import PIL" &> /dev/null; then
        print_success "Pillow is installed"
    else
        print_warning "Pillow is not installed"
        print_info "Run: pip install -r $REQUIREMENTS_FILE"

        read -p "Install dependencies now? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            print_error "Dependencies are required to continue"
            exit 1
        fi
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies from $REQUIREMENTS_FILE..."

    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        $PYTHON_CMD -m pip install -r "$REQUIREMENTS_FILE"
        print_success "Dependencies installed successfully"
    else
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "OPTIONS:"
    echo "  -f, --force        Force overwrite existing files"
    echo "  -v, --verbose      Enable verbose output"
    echo "  -q, --quick        Quick pack without dependency checks"
    echo "  -i, --install      Install dependencies and exit"
    echo "  -s, --stats        Show existing pack statistics"
    echo "  -c, --clean        Clean output directory before packing"
    echo "  -h, --help         Show this help message"
    echo
    echo "EXAMPLES:"
    echo "  $0                 # Basic pack with checks"
    echo "  $0 --force         # Force overwrite existing"
    echo "  $0 -fv             # Force + verbose"
    echo "  $0 --quick         # Skip checks for faster execution"
    echo
}

# Show statistics about existing packs
show_stats() {
    STATIC_DIR="$PROJECT_ROOT/website/static/wallpapers"
    MANIFEST_FILE="$STATIC_DIR/manifest.json"

    if [[ -f "$MANIFEST_FILE" ]]; then
        print_info "Reading existing pack statistics..."
        echo

        if command -v jq &> /dev/null; then
            # Use jq for pretty formatting if available
            TOTAL_PACKS=$(jq '.total_packs' "$MANIFEST_FILE")
            TOTAL_WALLPAPERS=$(jq '.total_wallpapers' "$MANIFEST_FILE")
            TOTAL_SIZE=$(jq '.total_size_mb' "$MANIFEST_FILE")
            GENERATED=$(jq -r '.generated' "$MANIFEST_FILE")

            echo -e "${BLUE}📊 Pack Statistics${NC}"
            echo "═══════════════════"
            echo "Total packs:      $TOTAL_PACKS"
            echo "Total wallpapers: $TOTAL_WALLPAPERS"
            echo "Total size:       ${TOTAL_SIZE} MB"
            echo "Generated:        $GENERATED"
            echo

            echo -e "${BLUE}📦 Available Packs${NC}"
            echo "═══════════════════"
            jq -r '.packs[] | "• \(.name) (\(.count) wallpapers, \(.size_mb) MB)"' "$MANIFEST_FILE"
        else
            # Fallback without jq
            print_info "Install 'jq' for better statistics formatting"
            cat "$MANIFEST_FILE"
        fi
    else
        print_warning "No existing manifest found. Run packer first."
    fi
}

# Clean output directory
clean_output() {
    STATIC_DIR="$PROJECT_ROOT/website/static/wallpapers"

    if [[ -d "$STATIC_DIR" ]]; then
        print_warning "This will delete all packed wallpapers in $STATIC_DIR"
        read -p "Are you sure? [y/N] " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Cleaning output directory..."
            rm -rf "$STATIC_DIR"
            print_success "Output directory cleaned"
        else
            print_info "Clean cancelled"
        fi
    else
        print_info "Output directory doesn't exist, nothing to clean"
    fi
}

# Main packing function
pack_wallpapers() {
    local force_flag=""
    local verbose_flag=""

    if [[ "$FORCE" == "true" ]]; then
        force_flag="--force"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        verbose_flag="--verbose"
    fi

    print_info "Starting wallpaper packing process..."
    print_info "Source: $PROJECT_ROOT/assets/Wallpapers"
    print_info "Output: $PROJECT_ROOT/website/static/wallpapers"
    echo

    # Run the packer script
    if $PYTHON_CMD "$PACKER_SCRIPT" $force_flag $verbose_flag; then
        print_success "Wallpaper packing completed successfully!"
        echo
        print_info "You can now:"
        print_info "• Start the website: cd website && python app.py"
        print_info "• Visit http://localhost:5000/wallpapers to test"
        print_info "• Check statistics: $0 --stats"
    else
        print_error "Wallpaper packing failed"
        exit 1
    fi
}

# Parse command line arguments
FORCE=false
VERBOSE=false
QUICK=false
INSTALL_ONLY=false
SHOW_STATS=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quick)
            QUICK=true
            shift
            ;;
        -i|--install)
            INSTALL_ONLY=true
            shift
            ;;
        -s|--stats)
            SHOW_STATS=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header

    # Handle special modes
    if [[ "$SHOW_STATS" == "true" ]]; then
        show_stats
        exit 0
    fi

    if [[ "$CLEAN" == "true" ]]; then
        clean_output
        if [[ "$INSTALL_ONLY" != "true" ]]; then
            echo
        fi
    fi

    # Check Python
    check_python

    # Install dependencies if requested
    if [[ "$INSTALL_ONLY" == "true" ]]; then
        install_dependencies
        print_success "Dependencies installed. You can now run the packer."
        exit 0
    fi

    # Check dependencies (unless quick mode)
    if [[ "$QUICK" != "true" ]]; then
        check_dependencies
    fi

    # Check if packer script exists
    if [[ ! -f "$PACKER_SCRIPT" ]]; then
        print_error "Packer script not found: $PACKER_SCRIPT"
        exit 1
    fi

    # Run the packing process
    pack_wallpapers
}

# Run main function
main "$@"
