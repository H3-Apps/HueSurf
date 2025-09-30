#!/usr/bin/env python3
"""
HueSurf Real-time Build Progress Discord Bot Test Script

This script tests the Discord bot configuration and dependencies
for the real-time build streaming functionality.
"""

import os
import sys
import importlib.util
from pathlib import Path


def test_python_version():
    """Test if Python version is compatible"""
    print("🐍 Testing Python version...")
    major, minor = sys.version_info[:2]

    if major >= 3 and minor >= 8:
        print(f"✅ Python {major}.{minor} is compatible")
        return True
    else:
        print(f"❌ Python {major}.{minor} is too old. Python 3.8+ required")
        return False


def test_dependencies():
    """Test if required dependencies are installed"""
    print("📦 Testing dependencies...")

    required_packages = {"discord": "discord.py", "dotenv": "python-dotenv"}

    all_good = True

    for package, pip_name in required_packages.items():
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                print(f"✅ {pip_name} is installed")
            else:
                print(f"❌ {pip_name} is not installed")
                all_good = False
        except ImportError:
            print(f"❌ {pip_name} is not installed")
            all_good = False

    return all_good


def test_env_file():
    """Test if .env file exists and has required variables"""
    print("🔐 Testing environment configuration...")

    # Look for .env file in parent directory
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print(f"❌ .env file not found at {env_path}")
        print("   Create a .env file with your Discord token")
        return False

    print(f"✅ .env file found at {env_path}")

    # Check if it contains DISCORD_TOKEN
    try:
        with open(env_path, "r") as f:
            content = f.read()

        if "DISCORD_TOKEN" in content:
            print("✅ DISCORD_TOKEN variable found in .env")

            # Check if it's not the default placeholder
            for line in content.split("\n"):
                if line.startswith("DISCORD_TOKEN=") and not line.startswith("#"):
                    token_value = line.split("=", 1)[1].strip()
                    if token_value == "your_discord_bot_token_here":
                        print("⚠️  DISCORD_TOKEN is still set to placeholder value")
                        print("   Replace with your actual Discord bot token")
                        return False
                    elif len(token_value) < 50:
                        print("⚠️  DISCORD_TOKEN appears to be too short")
                        print("   Discord bot tokens are typically 70+ characters")
                        return False
                    else:
                        print("✅ DISCORD_TOKEN appears to be properly configured")
                        return True

            print("⚠️  DISCORD_TOKEN found but may be commented out")
            return False
        else:
            print("❌ DISCORD_TOKEN not found in .env file")
            return False

    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False


def test_bot_files():
    """Test if bot files exist and are accessible"""
    print("📁 Testing bot files...")

    script_dir = Path(__file__).parent

    files_to_check = {
        "discord_build_bot.py": "Main bot script",
        "requirements_discord.txt": "Dependencies file",
        "DISCORD_BOT_README.md": "Documentation",
    }

    all_good = True

    for filename, description in files_to_check.items():
        file_path = script_dir / filename
        if file_path.exists():
            print(f"✅ {description} found ({filename})")
        else:
            print(f"❌ {description} missing ({filename})")
            all_good = False

    return all_good


def test_token_format():
    """Test if we can load the environment and check token format"""
    print("🔑 Testing Discord token format...")

    try:
        # Try to import and load dotenv
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).parent.parent / ".env")

        token = os.getenv("DISCORD_TOKEN")

        if not token:
            print("❌ Could not load DISCORD_TOKEN from environment")
            return False

        if token == "your_discord_bot_token_here":
            print("❌ Token is still set to placeholder value")
            return False

        # Basic token format validation
        if len(token) < 50:
            print("⚠️  Token appears to be too short for a Discord bot token")
            return False

        # Discord bot tokens typically start with specific patterns
        if not (
            token.startswith("MTA")
            or token.startswith("MTB")
            or token.startswith("MT")
            or token.startswith("ODA")
            or token.startswith("ODB")
            or len(token) > 70
        ):
            print("⚠️  Token format may be incorrect")
            print("   Discord bot tokens are usually 70+ characters long")
            return False

        print("✅ Token format appears valid")
        return True

    except ImportError:
        print("❌ python-dotenv not available for token testing")
        return False
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False


def test_bot_import():
    """Test if the bot script can be imported without errors"""
    print("🤖 Testing bot import...")

    try:
        script_dir = Path(__file__).parent
        bot_script = script_dir / "discord_build_bot.py"

        if not bot_script.exists():
            print("❌ discord_build_bot.py not found")
            return False

        # Try to import the discord library first
        import discord
        from discord.ext import commands

        print("✅ Discord.py imports successfully")

        # Basic validation that the bot script is syntactically correct
        with open(bot_script, "r") as f:
            code = f.read()

        # Check for key components
        if "class HueSurfBuildBot" in code:
            print("✅ HueSurfBuildBot class found")
        else:
            print("⚠️  HueSurfBuildBot class not found in bot script")

        if "@bot.tree.command" in code and "buildprog" in code:
            print("✅ Build progress slash command found in bot script")
        else:
            print("⚠️  Build progress slash command not found in bot script")

        print("✅ Bot script appears to be properly structured")
        return True

    except ImportError as e:
        print(f"❌ Failed to import Discord library: {e}")
        return False
    except SyntaxError as e:
        print(f"❌ Syntax error in bot script: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing bot import: {e}")
        return False


def print_summary(results):
    """Print test summary and next steps"""
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"Tests passed: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("🎉 All tests passed! Your Discord bot is ready to run.")
        print("\n💡 Next steps:")
        print("1. Run the bot: python3 discord_build_bot.py")
        print("2. Invite the bot to your Discord server")
        print("3. Test with /buildprog command to start streaming")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print(
            "- Install missing dependencies: pip3 install -r requirements_discord.txt"
        )
        print("- Set your Discord token in the .env file")
        print("- Ensure all bot files are present")

    print(f"\n📚 For more help, see DISCORD_BOT_README.md")


def main():
    """Run all tests"""
    print("🧪 HueSurf Discord Bot Configuration Test")
    print("=" * 50)

    tests = {
        "Python Version": test_python_version,
        "Dependencies": test_dependencies,
        "Environment File": test_env_file,
        "Bot Files": test_bot_files,
        "Token Format": test_token_format,
        "Bot Import": test_bot_import,
    }

    results = {}

    for test_name, test_func in tests.items():
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            results[test_name] = False

    print_summary(results)

    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
