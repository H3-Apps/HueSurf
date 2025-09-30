#!/bin/bash

# HueSurf Bedtime Build Script
#
# A simple wrapper to start your overnight build before going to bed.
# This script prevents your Mac from sleeping and runs the HueSurf build process.
#
# Usage:
#   ./bedtime_build.sh                    # Standard build
#   ./bedtime_build.sh --with-discord     # Build with Discord notifications
#   ./bedtime_build.sh --fast-test        # Quick test build
#   ./bedtime_build.sh --full             # Full build with all features
#
# The script will:
# - Prevent your MacBook from sleeping
# - Run the HueSurf build process
# - Log everything to overnight_build.log
# - Send notifications when complete
# - Restore sleep settings when done

set -e

# Default configuration
BUILD_COMMAND="scripts/build.sh"
USE_DISCORD=false
USE_NOTIFICATIONS=true
FAST_MODE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🌙 HueSurf Bedtime Build                  ║"
    echo "║                                                              ║"
    echo "║  Sweet dreams! Your MacBook will build HueSurf overnight.   ║"
    echo "║  You'll wake up to a fresh browser build! 🛠️✨             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --with-discord|-d)
            USE_DISCORD=true
            print_status "Discord notifications enabled"
            ;;
        --fast-test|-f)
            BUILD_COMMAND="scripts/example-build.sh --fast"
            FAST_MODE=true
            print_status "Fast test mode enabled"
            ;;
        --no-notifications|-n)
            USE_NOTIFICATIONS=false
            print_status "System notifications disabled"
            ;;
        --full)
            USE_DISCORD=true
            USE_NOTIFICATIONS=true
            print_status "Full feature mode enabled"
            ;;
        --help|-h)
            echo "🌙 HueSurf Bedtime Build Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --with-discord, -d     Enable Discord bot notifications"
            echo "  --fast-test, -f        Run fast test build (for testing)"
            echo "  --no-notifications, -n Disable system notifications"
            echo "  --full                 Enable all features"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     # Standard overnight build"
            echo "  $0 --with-discord      # Build with Discord updates"
            echo "  $0 --fast-test         # Quick 30-second test build"
            echo "  $0 --full              # All features enabled"
            exit 0
            ;;
        *)
            print_error "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Change to script directory
cd "$(dirname "$0")"

print_header

# Pre-flight checks
print_status "Running pre-flight checks..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not found"
    print_status "Install Python 3: https://python.org/downloads/"
    exit 1
fi

# Check if caffeinate is available (should be on all macOS systems)
if ! command -v caffeinate &> /dev/null; then
    print_warning "caffeinate not found - sleep prevention may not work"
fi

# Check if overnight_build.py exists
if [[ ! -f "overnight_build.py" ]]; then
    print_error "overnight_build.py not found in current directory"
    exit 1
fi

# Check if build script exists (unless it's the example)
if [[ "$BUILD_COMMAND" != "scripts/example-build.sh --fast" ]]; then
    if [[ ! -f "../$BUILD_COMMAND" ]]; then
        print_error "Build script not found: $BUILD_COMMAND"
        print_status "Available build scripts:"
        find .. -name "*.sh" -path "*/scripts/*" | sed 's|^\.\./||' | head -5
        exit 1
    fi
fi

print_success "Pre-flight checks passed"

# Show configuration
echo ""
print_status "📋 Build Configuration:"
echo "  🛠️  Build command: $BUILD_COMMAND"
echo "  🤖 Discord bot: $([ "$USE_DISCORD" = true ] && echo "✅ Enabled" || echo "❌ Disabled")"
echo "  📱 Notifications: $([ "$USE_NOTIFICATIONS" = true ] && echo "✅ Enabled" || echo "❌ Disabled")"
echo "  ⚡ Fast mode: $([ "$FAST_MODE" = true ] && echo "✅ Yes" || echo "❌ No")"

# Time estimates
if [[ "$FAST_MODE" = true ]]; then
    echo "  ⏱️  Estimated time: ~30 seconds"
else
    echo "  ⏱️  Estimated time: 1-3 hours"
fi

echo "  📝 Log file: overnight_build.log"
echo ""

# Battery check
battery_level=$(pmset -g batt | grep -o '[0-9]*%' | head -1 | tr -d '%')
if [[ -n "$battery_level" && "$battery_level" -lt 20 ]]; then
    print_warning "Battery level is low ($battery_level%)"
    print_status "Consider plugging in your MacBook for overnight builds"
    echo -n "Continue anyway? (y/N): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Build cancelled - plug in and try again"
        exit 0
    fi
fi

# Final confirmation
echo ""
if [[ "$FAST_MODE" = true ]]; then
    print_status "🚀 Ready to start fast test build!"
    echo -n "Press Enter to start the 30-second test build, or Ctrl+C to cancel... "
else
    print_status "🌙 Ready to start overnight build!"
    print_status "Your MacBook will stay awake and build HueSurf overnight."
    print_status "You can safely close the laptop lid - it won't sleep."
    echo ""
    echo -n "Press Enter to start the overnight build, or Ctrl+C to cancel... "
fi

read -r

# Build Python command
python_args="--command \"$BUILD_COMMAND\""

if [[ "$USE_DISCORD" = true ]]; then
    python_args="$python_args --discord"
fi

if [[ "$USE_NOTIFICATIONS" = true ]]; then
    python_args="$python_args --notify"
fi

# Start the build
echo ""
print_success "Starting overnight build system..."
print_status "You can now close your laptop lid and go to sleep! 💤"

# Run the Python script
eval "python3 overnight_build.py $python_args"

# Capture exit code
exit_code=$?

# Final message
echo ""
if [[ $exit_code -eq 0 ]]; then
    print_success "🎉 Build completed successfully!"
    if [[ "$FAST_MODE" != true ]]; then
        print_success "Good morning! Your HueSurf browser is ready! ☀️"
    fi
else
    print_error "Build failed or was interrupted"
    print_status "Check overnight_build.log for details"
fi

print_status "Sleep settings have been restored"
print_status "Have a great day! 🌟"

exit $exit_code
