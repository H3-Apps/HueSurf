#!/usr/bin/env python3
"""
HueSurf Easy Build Script
A "build script for dummies" that simplifies the build process with an interactive menu.
"""

import os
import sys
import subprocess
import shutil

# pylint: disable=too-few-public-methods
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Clears screen and prints the header."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.HEADER}======================================={Colors.ENDC}")
    print(f"{Colors.HEADER}   🌊 HueSurf Easy Build System{Colors.ENDC}")
    print(f"{Colors.HEADER}   Simple build tool for everyone{Colors.ENDC}")
    print(f"{Colors.HEADER}======================================={Colors.ENDC}")
    print()

def run_script(script_name, args=None):
    """Runs a shell script and handles errors."""
    if args is None:
        args = []

    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, script_name)

    if not os.path.exists(full_path):
        print(f"{Colors.FAIL}Error: Script not found: {full_path}{Colors.ENDC}")
        return False

    cmd = [full_path] + args
    print(f"{Colors.BLUE}Running: {' '.join(cmd)}...{Colors.ENDC}")
    print()

    try:
        # Use simple subprocess call to let the script take over stdout/stdin
        result = subprocess.call(cmd)
        if result == 0:
            return True
        print(f"\n{Colors.FAIL}Command failed with exit code {result}{Colors.ENDC}")
        return False
    except OSError as e:
        print(f"\n{Colors.FAIL}Error running script: {e}{Colors.ENDC}")
        return False

def clean_build():
    """Cleans the build directory."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.join(project_root, "chromium_src", "src", "out")

    print(f"{Colors.WARNING}This will remove the build directory: {out_dir}{Colors.ENDC}")
    confirm = input("Are you sure? (y/N): ").strip().lower()

    if confirm == 'y':
        if os.path.exists(out_dir):
            print(f"{Colors.BLUE}Removing {out_dir}...{Colors.ENDC}")
            try:
                shutil.rmtree(out_dir)
                print(f"{Colors.GREEN}✅ Clean complete.{Colors.ENDC}")
            except OSError as e:
                print(f"{Colors.FAIL}Error removing directory: {e}{Colors.ENDC}")
        else:
            print(f"{Colors.BLUE}Directory does not exist. Nothing to clean.{Colors.ENDC}")
    else:
        print("Clean cancelled.")

    input(f"\n{Colors.BLUE}Press Enter to return to menu...{Colors.ENDC}")

def main():
    """Main menu loop."""
    while True:
        print_header()
        print(f"{Colors.BOLD}Select an option:{Colors.ENDC}")
        print()
        print(f"{Colors.GREEN}1. 🚀 Build HueSurf (Standard){Colors.ENDC}")
        print("   Downloads source, patches, and builds the browser.")
        print("   This takes a long time (1-4 hours).")
        print()
        print(f"{Colors.BLUE}2. 🧪 Quick Test Build (Simulation){Colors.ENDC}")
        print("   Simulates the build process in ~30 seconds.")
        print("   Use this to see how the build system works.")
        print()
        print(f"{Colors.BLUE}3. 📦 Pack Wallpapers{Colors.ENDC}")
        print("   Prepares wallpapers for the website.")
        print()
        print(f"{Colors.WARNING}4. 🧹 Clean Build Files{Colors.ENDC}")
        print("   Frees up disk space by removing build artifacts.")
        print()
        print(f"{Colors.FAIL}5. ❌ Exit{Colors.ENDC}")
        print()

        choice = input(f"{Colors.BOLD}Enter choice [1-5]: {Colors.ENDC}").strip()

        if choice == '1':
            print(f"\n{Colors.GREEN}Starting Standard Build...{Colors.ENDC}")
            run_script("build.sh")
            input(f"\n{Colors.BLUE}Press Enter to return to menu...{Colors.ENDC}")
        elif choice == '2':
            print(f"\n{Colors.BLUE}Starting Quick Test Build...{Colors.ENDC}")
            run_script("example-build.sh", ["--fast"])
            input(f"\n{Colors.BLUE}Press Enter to return to menu...{Colors.ENDC}")
        elif choice == '3':
            print(f"\n{Colors.BLUE}Starting Wallpaper Packer...{Colors.ENDC}")
            run_script("pack.sh")
            input(f"\n{Colors.BLUE}Press Enter to return to menu...{Colors.ENDC}")
        elif choice == '4':
            clean_build()
        elif choice == '5':
            print(f"\n{Colors.GREEN}Goodbye! 👋{Colors.ENDC}")
            sys.exit(0)
        else:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GREEN}Goodbye! 👋{Colors.ENDC}")
        sys.exit(0)
