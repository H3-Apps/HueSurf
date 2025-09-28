#!/bin/bash

# HueSurf Google Services Removal Validation Script
# Validates that patch 002-remove-google-services.patch was applied successfully
#
# Made with 💚 by the HueSurf team - because your data should stay yours!

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Base directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHROMIUM_SRC="$PROJECT_ROOT/chromium_src/src"

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}🕵️  HueSurf Google Services Removal Validator${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_section() {
    echo -e "${YELLOW}🔍 $1${NC}"
    echo "----------------------------------------"
}

check_pass() {
    echo -e "  ✅ ${GREEN}$1${NC}"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "  ❌ ${RED}$1${NC}"
    ((CHECKS_FAILED++))
}

check_warning() {
    echo -e "  ⚠️  ${YELLOW}$1${NC}"
    ((WARNINGS++))
}

check_chromium_source() {
    print_section "Checking Chromium Source Directory"

    if [ ! -d "$CHROMIUM_SRC" ]; then
        check_fail "Chromium source not found at $CHROMIUM_SRC"
        echo -e "${RED}Please run './scripts/build.sh fetch' first to download Chromium source${NC}"
        exit 1
    fi

    check_pass "Chromium source directory exists"
    echo ""
}

check_google_branding_removal() {
    print_section "Validating Google Branding Removal"

    # Check google_brand.cc
    if [ -f "$CHROMIUM_SRC/chrome/browser/google/google_brand.cc" ]; then
        if grep -q 'brand->assign("")' "$CHROMIUM_SRC/chrome/browser/google/google_brand.cc"; then
            check_pass "Google brand strings disabled in google_brand.cc"
        else
            check_fail "Google branding not properly removed from google_brand.cc"
        fi
    else
        check_warning "google_brand.cc not found - may not exist in this Chromium version"
    fi

    # Check for HueSurf branding
    if [ -f "$CHROMIUM_SRC/chrome/app/theme/chromium/BRANDING" ]; then
        if grep -q "HueSurf" "$CHROMIUM_SRC/chrome/app/theme/chromium/BRANDING"; then
            check_pass "HueSurf branding properly set in BRANDING file"
        else
            check_fail "HueSurf branding not found in BRANDING file"
        fi
    else
        check_warning "BRANDING file not found"
    fi

    echo ""
}

check_google_urls_disabled() {
    print_section "Validating Google URL Disabling"

    # Check google_util.cc
    if [ -f "$CHROMIUM_SRC/components/google/core/common/google_util.cc" ]; then
        if grep -q "return false" "$CHROMIUM_SRC/components/google/core/common/google_util.cc"; then
            check_pass "Google URL detection disabled in google_util.cc"
        else
            check_fail "Google URL detection not properly disabled"
        fi
    else
        check_warning "google_util.cc not found"
    fi

    echo ""
}

check_search_engines() {
    print_section "Validating Search Engine Configuration"

    # Check prepopulated engines
    if [ -f "$CHROMIUM_SRC/components/search_engines/prepopulated_engines.json" ]; then
        if ! grep -q '"google":' "$CHROMIUM_SRC/components/search_engines/prepopulated_engines.json"; then
            check_pass "Google search engine removed from prepopulated engines"
        else
            check_fail "Google search engine still present in prepopulated engines"
        fi

        if grep -q "duckduckgo" "$CHROMIUM_SRC/components/search_engines/prepopulated_engines.json"; then
            check_pass "DuckDuckGo search engine configured"
        else
            check_warning "DuckDuckGo not found in search engines"
        fi
    else
        check_warning "prepopulated_engines.json not found"
    fi

    echo ""
}

check_google_services_disabled() {
    print_section "Validating Google Services Disabling"

    # Check for disabled services in various files
    local service_files=(
        "chrome/browser/safe_browsing/safe_browsing_service.cc"
        "chrome/browser/signin/signin_manager_factory.cc"
        "components/sync/driver/sync_service_impl.cc"
        "components/gcm_driver/gcm_driver_desktop.cc"
        "components/translate/core/browser/translate_manager.cc"
    )

    for file in "${service_files[@]}"; do
        if [ -f "$CHROMIUM_SRC/$file" ]; then
            if grep -q "HueSurf:" "$CHROMIUM_SRC/$file" && grep -q "return" "$CHROMIUM_SRC/$file"; then
                check_pass "Google services disabled in $(basename "$file")"
            else
                check_fail "Google services not properly disabled in $(basename "$file")"
            fi
        else
            check_warning "$(basename "$file") not found - may not exist in this version"
        fi
    done

    echo ""
}

check_command_line_switches() {
    print_section "Validating Command Line Switches"

    if [ -f "$CHROMIUM_SRC/chrome/browser/chrome_browser_main.cc" ]; then
        local switches=(
            "disable-background-networking"
            "disable-google-now-integration"
            "disable-speech-api"
            "disable-sync"
            "disable-translate"
        )

        for switch in "${switches[@]}"; do
            if grep -q "$switch" "$CHROMIUM_SRC/chrome/browser/chrome_browser_main.cc"; then
                check_pass "Command line switch '$switch' added"
            else
                check_fail "Command line switch '$switch' missing"
            fi
        done
    else
        check_warning "chrome_browser_main.cc not found"
    fi

    echo ""
}

check_extension_removal() {
    print_section "Validating Google Extension Removal"

    if [ -f "$CHROMIUM_SRC/chrome/browser/extensions/component_loader.cc" ]; then
        if grep -q "/\* HueSurf: Skip Google Hangout Services" "$CHROMIUM_SRC/chrome/browser/extensions/component_loader.cc"; then
            check_pass "Google Hangout Services extension disabled"
        else
            check_fail "Google Hangout Services extension not properly disabled"
        fi
    else
        check_warning "component_loader.cc not found"
    fi

    echo ""
}

check_configuration_alignment() {
    print_section "Validating Configuration Alignment"

    local config_file="$PROJECT_ROOT/config/custom_args.gn"
    if [ -f "$config_file" ]; then
        local config_checks=(
            "use_official_google_api_keys = false"
            "enable_google_now_integration = false"
            "enable_hangout_services_extension = false"
            "safe_browsing_mode = 0"
            "enable_google_update_integration = false"
        )

        for check in "${config_checks[@]}"; do
            if grep -q "$check" "$config_file"; then
                check_pass "Configuration: $check"
            else
                check_fail "Missing configuration: $check"
            fi
        done
    else
        check_fail "custom_args.gn configuration file not found"
    fi

    echo ""
}

check_no_google_domains() {
    print_section "Scanning for Remaining Google Domain References"

    # Look for common Google domains in source files
    local google_domains=(
        "google.com"
        "googleapis.com"
        "gstatic.com"
        "googleusercontent.com"
        "googlesyndication.com"
        "doubleclick.net"
    )

    local found_domains=0

    for domain in "${google_domains[@]}"; do
        if [ -d "$CHROMIUM_SRC" ]; then
            # Count occurrences, excluding comments and test files
            local count=$(find "$CHROMIUM_SRC" -name "*.cc" -o -name "*.h" -o -name "*.json" | \
                         xargs grep -l "$domain" 2>/dev/null | \
                         grep -v test | grep -v Test | wc -l || echo "0")

            if [ "$count" -gt 0 ]; then
                check_warning "$count files still reference $domain (may be legitimate)"
                ((found_domains++))
            fi
        fi
    done

    if [ "$found_domains" -eq 0 ]; then
        check_pass "No suspicious Google domain references found"
    fi

    echo ""
}

print_summary() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}📊 Validation Summary${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo -e "✅ ${GREEN}Checks Passed: $CHECKS_PASSED${NC}"
    echo -e "❌ ${RED}Checks Failed: $CHECKS_FAILED${NC}"
    echo -e "⚠️  ${YELLOW}Warnings: $WARNINGS${NC}"
    echo ""

    if [ "$CHECKS_FAILED" -eq 0 ]; then
        echo -e "🎉 ${GREEN}SUCCESS: Google services removal validation passed!${NC}"
        echo -e "${GREEN}Your HueSurf build should be free of Google integrations.${NC}"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo -e "  1. Run './scripts/build.sh build' to compile HueSurf"
        echo -e "  2. Test the browser to ensure functionality"
        echo -e "  3. Verify no network requests to Google domains"
    else
        echo -e "💥 ${RED}FAILED: Google services removal validation failed!${NC}"
        echo -e "${RED}Please check the failed items above and re-apply patches.${NC}"
        echo ""
        echo -e "${BLUE}To fix issues:${NC}"
        echo -e "  1. Run './scripts/build.sh clean'"
        echo -e "  2. Run './scripts/build.sh patch'"
        echo -e "  3. Re-run this validation script"
        exit 1
    fi

    if [ "$WARNINGS" -gt 0 ]; then
        echo -e "${YELLOW}Note: Warnings are usually fine - they often indicate version differences.${NC}"
    fi

    echo ""
    echo -e "${BLUE}Made with 💚 by the HueSurf team${NC}"
    echo -e "${BLUE}Privacy-focused browsing without the Google bloat!${NC}"
}

# Main execution
main() {
    print_header

    check_chromium_source
    check_google_branding_removal
    check_google_urls_disabled
    check_search_engines
    check_google_services_disabled
    check_command_line_switches
    check_extension_removal
    check_configuration_alignment
    check_no_google_domains

    print_summary
}

# Run the validation
main "$@"
