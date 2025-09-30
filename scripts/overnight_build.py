#!/usr/bin/env python3
"""
HueSurf Overnight Build Script

This script prevents your MacBook from sleeping and runs the HueSurf build process.
Perfect for running long builds overnight while you sleep!

Features:
- Prevents macOS from sleeping during build
- Runs build command with full logging
- Integrates with Discord bot (optional)
- Shows progress and status updates
- Handles interruptions gracefully
- Sends completion notifications

Usage:
    python3 overnight_build.py [--command COMMAND] [--discord] [--notify] [--log-file FILE]

Examples:
    python3 overnight_build.py
    python3 overnight_build.py --command "scripts/build.sh"
    python3 overnight_build.py --discord --notify
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading
import json

# Default configuration
DEFAULT_BUILD_COMMAND = "scripts/build.sh"
DEFAULT_LOG_FILE = "overnight_build.log"
DISCORD_BOT_SCRIPT = "scripts/discord_build_bot.py"


class OvernightBuilder:
    def __init__(
        self, build_command, log_file, use_discord=False, send_notifications=False
    ):
        self.build_command = build_command
        self.log_file = log_file
        self.use_discord = use_discord
        self.send_notifications = send_notifications
        self.start_time = None
        self.caffeinate_process = None
        self.build_process = None
        self.discord_process = None
        self.interrupted = False

        # Setup logging
        self.setup_logging()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_logging(self):
        """Setup logging to both file and console"""
        # Create logs directory if it doesn't exist
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.interrupted = True
        self.cleanup()
        sys.exit(0)

    def send_system_notification(self, title, message):
        """Send macOS system notification"""
        if self.send_notifications:
            try:
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        f'display notification "{message}" with title "{title}"',
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                self.logger.warning("Failed to send system notification")

    def prevent_sleep(self):
        """Prevent macOS from sleeping using caffeinate"""
        try:
            self.logger.info("🔋 Preventing system sleep with caffeinate...")
            # caffeinate -d prevents display sleep, -i prevents idle sleep
            self.caffeinate_process = subprocess.Popen(
                ["caffeinate", "-d", "-i"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.logger.info("✅ System sleep prevention activated")
            return True
        except FileNotFoundError:
            self.logger.error("❌ caffeinate command not found (are you on macOS?)")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to prevent sleep: {e}")
            return False

    def start_discord_bot(self):
        """Start Discord bot if requested and available"""
        if not self.use_discord:
            return None

        discord_script = Path(DISCORD_BOT_SCRIPT)
        if not discord_script.exists():
            self.logger.warning(f"Discord bot script not found: {discord_script}")
            return None

        # Check if .env file exists
        env_file = Path("../.env")
        if not env_file.exists():
            self.logger.warning(
                "Discord bot .env file not found, skipping Discord integration"
            )
            return None

        try:
            self.logger.info("🤖 Starting Discord bot...")
            self.discord_process = subprocess.Popen(
                ["python3", str(discord_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(discord_script.parent),
            )

            # Give bot time to start
            time.sleep(3)

            if self.discord_process.poll() is None:
                self.logger.info("✅ Discord bot started successfully")
                return self.discord_process
            else:
                self.logger.error("❌ Discord bot failed to start")
                return None

        except Exception as e:
            self.logger.error(f"❌ Failed to start Discord bot: {e}")
            return None

    def run_build(self):
        """Run the build command"""
        try:
            # Change to HueSurf root directory
            build_dir = Path(__file__).parent.parent
            os.chdir(build_dir)

            self.logger.info(f"🛠️  Starting build command: {self.build_command}")
            self.logger.info(f"📁 Working directory: {os.getcwd()}")

            # Start build process
            self.build_process = subprocess.Popen(
                self.build_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # Stream output in real-time
            while True:
                output = self.build_process.stdout.readline()
                if output == "" and self.build_process.poll() is not None:
                    break

                if output:
                    # Log to file and potentially Discord
                    output_line = output.strip()
                    self.logger.info(f"BUILD: {output_line}")

            # Wait for process to complete
            return_code = self.build_process.wait()

            if return_code == 0:
                self.logger.info("✅ Build completed successfully!")
                return True
            else:
                self.logger.error(f"❌ Build failed with exit code {return_code}")
                return False

        except FileNotFoundError:
            self.logger.error(f"❌ Build command not found: {self.build_command}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Build error: {e}")
            return False

    def estimate_completion_time(self):
        """Estimate build completion time based on progress"""
        if not self.start_time:
            return "Unknown"

        elapsed = datetime.now() - self.start_time
        # This is a rough estimate - could be improved with actual progress tracking
        estimated_total = timedelta(hours=2)  # Assume 2-hour build time
        estimated_completion = self.start_time + estimated_total

        return estimated_completion.strftime("%I:%M %p")

    def cleanup(self):
        """Clean up processes and restore system state"""
        self.logger.info("🧹 Cleaning up...")

        # Terminate build process
        if self.build_process and self.build_process.poll() is None:
            self.logger.info("Stopping build process...")
            self.build_process.terminate()
            try:
                self.build_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.build_process.kill()

        # Stop Discord bot
        if self.discord_process and self.discord_process.poll() is None:
            self.logger.info("Stopping Discord bot...")
            self.discord_process.terminate()
            try:
                self.discord_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.discord_process.kill()

        # Stop caffeinate (restore sleep)
        if self.caffeinate_process and self.caffeinate_process.poll() is None:
            self.logger.info("Restoring system sleep settings...")
            self.caffeinate_process.terminate()
            try:
                self.caffeinate_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.caffeinate_process.kill()

        self.logger.info("✅ Cleanup completed")

    def create_build_summary(self, success, duration):
        """Create build summary report"""
        summary = {
            "build_command": self.build_command,
            "start_time": self.start_time.isoformat(),
            "duration": str(duration),
            "success": success,
            "log_file": self.log_file,
        }

        summary_file = f"build_summary_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return summary_file

    def run(self):
        """Main execution method"""
        self.start_time = datetime.now()

        # Print startup banner
        print("=" * 60)
        print("🌙 HueSurf Overnight Build System")
        print("=" * 60)
        print(f"⏰ Start time: {self.start_time.strftime('%Y-%m-%d %I:%M:%S %p')}")
        print(f"🛠️  Build command: {self.build_command}")
        print(f"📝 Log file: {self.log_file}")
        print(f"🤖 Discord integration: {'✅' if self.use_discord else '❌'}")
        print(f"📱 System notifications: {'✅' if self.send_notifications else '❌'}")
        print("=" * 60)

        self.logger.info("🌙 Starting overnight build system...")

        # Send start notification
        self.send_system_notification(
            "HueSurf Build Started",
            f"Overnight build started at {self.start_time.strftime('%I:%M %p')}",
        )

        success = False

        try:
            # Step 1: Prevent sleep
            if not self.prevent_sleep():
                self.logger.error(
                    "Failed to prevent system sleep, build may be interrupted"
                )
                if not self.ask_continue():
                    return False

            # Step 2: Start Discord bot (optional)
            if self.use_discord:
                self.start_discord_bot()

            # Step 3: Run the build
            self.logger.info(f"🚀 Starting build process...")
            self.logger.info(
                f"🕐 Estimated completion: {self.estimate_completion_time()}"
            )

            success = self.run_build()

        except KeyboardInterrupt:
            self.logger.info("🛑 Build interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
        finally:
            # Always cleanup
            end_time = datetime.now()
            duration = end_time - self.start_time

            # Create summary
            summary_file = self.create_build_summary(success, duration)

            # Final logging
            self.logger.info("=" * 50)
            self.logger.info("🏁 Build session completed")
            self.logger.info(f"⏱️  Duration: {duration}")
            self.logger.info(f"🎯 Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
            self.logger.info(f"📊 Summary: {summary_file}")
            self.logger.info("=" * 50)

            # Send completion notification
            result_emoji = "✅" if success else "❌"
            result_text = "completed successfully" if success else "failed"

            self.send_system_notification(
                f"HueSurf Build {result_emoji}", f"Build {result_text} after {duration}"
            )

            # Cleanup
            self.cleanup()

        return success

    def ask_continue(self):
        """Ask user if they want to continue despite issues"""
        try:
            response = (
                input("\nDo you want to continue anyway? (y/N): ").strip().lower()
            )
            return response in ["y", "yes"]
        except KeyboardInterrupt:
            return False


def main():
    parser = argparse.ArgumentParser(
        description="HueSurf Overnight Build System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 overnight_build.py
  python3 overnight_build.py --command "scripts/build.sh"
  python3 overnight_build.py --discord --notify
  python3 overnight_build.py --command "scripts/example-build.sh --fast"
        """,
    )

    parser.add_argument(
        "--command",
        "-c",
        default=DEFAULT_BUILD_COMMAND,
        help=f"Build command to run (default: {DEFAULT_BUILD_COMMAND})",
    )

    parser.add_argument(
        "--log-file",
        "-l",
        default=DEFAULT_LOG_FILE,
        help=f"Log file path (default: {DEFAULT_LOG_FILE})",
    )

    parser.add_argument(
        "--discord",
        "-d",
        action="store_true",
        help="Start Discord bot for real-time updates",
    )

    parser.add_argument(
        "--notify", "-n", action="store_true", help="Send macOS system notifications"
    )

    args = parser.parse_args()

    # Validate build command exists
    if not args.command.startswith("scripts/"):
        script_path = Path(args.command)
    else:
        script_path = Path("..") / args.command

    if not script_path.exists() and not args.command.startswith(
        "scripts/example-build.sh"
    ):
        print(f"❌ Build script not found: {script_path}")
        print("Available scripts:")
        scripts_dir = Path("../scripts")
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.sh"):
                print(f"  - scripts/{script.name}")
        sys.exit(1)

    # Create and run builder
    builder = OvernightBuilder(
        build_command=args.command,
        log_file=args.log_file,
        use_discord=args.discord,
        send_notifications=args.notify,
    )

    # Final confirmation
    print(f"\n🌙 Ready to start overnight build!")
    print(f"📋 Command: {args.command}")
    print(f"📝 Logs: {args.log_file}")
    print(f"🔋 Sleep prevention: Enabled")

    try:
        response = input("\nPress Enter to start, or Ctrl+C to cancel... ")
        success = builder.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Build cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
