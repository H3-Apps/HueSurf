#!/usr/bin/env python3
"""
HueSurf Real-time Build Progress Discord Bot

This bot streams real-time console logs and build progress to Discord.
Commands:
  /buildprog - Start streaming build progress and console output
"""

import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import logging
import subprocess
import threading
import time
from collections import deque
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True


class HueSurfBuildBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.build_message = None
        self.build_channel = None
        self.is_streaming = False
        self.build_process = None
        self.log_buffer = deque(maxlen=50)  # Keep last 50 lines
        self.progress_percentage = 0
        self.build_status = "Idle"

    async def on_ready(self):
        logger.info(f"{self.user} has connected to Discord!")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")


bot = HueSurfBuildBot()


def extract_progress_from_line(line):
    """Extract progress percentage from build output line"""
    # Common progress patterns in build systems
    patterns = [
        r"(\d+)%",  # Direct percentage
        r"\[(\d+)/(\d+)\]",  # [current/total] format
        r"(\d+) of (\d+)",  # X of Y format
        r"Progress: (\d+)%",  # Progress: X%
        r"Building.*?(\d+)%",  # Building... X%
    ]

    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            if len(match.groups()) == 1:
                return int(match.group(1))
            elif len(match.groups()) == 2:
                # Calculate percentage from current/total
                current, total = int(match.group(1)), int(match.group(2))
                return int((current / total) * 100) if total > 0 else 0

    return None


def create_build_embed(status, percentage, log_lines):
    """Create an embed for build status with console output"""

    # Determine color based on status and percentage
    if status == "Complete":
        color = discord.Color.green()
    elif status == "Error" or status == "Failed":
        color = discord.Color.red()
    elif status == "Building":
        color = discord.Color.yellow()
    else:
        color = discord.Color.blue()

    # Create progress bar
    filled_blocks = int(percentage / 5)  # 20 blocks total (100 / 5)
    empty_blocks = 20 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks

    embed = discord.Embed(
        title="🛠️ HueSurf Browser Build Progress",
        description=f"**Status:** {status}\n**Progress:** {percentage}%",
        color=color,
        timestamp=discord.utils.utcnow(),
    )

    # Add progress bar
    embed.add_field(
        name="Progress",
        value=f"```\n{progress_bar} {percentage}%\n```",
        inline=False,
    )

    # Add recent console output (limited to avoid Discord limits)
    if log_lines:
        # Take last few lines and limit total character count
        recent_lines = list(log_lines)[-15:]  # Last 15 lines
        console_output = "\n".join(recent_lines)

        # Truncate if too long (Discord embed field limit is 1024 chars)
        if len(console_output) > 1000:
            console_output = "..." + console_output[-997:]

        embed.add_field(
            name="🖥️ Console Output",
            value=f"```\n{console_output}\n```",
            inline=False,
        )

    embed.set_footer(text="HueSurf Build System • Live Stream")
    return embed


async def stream_build_process(interaction, build_command):
    """Stream build process output to Discord"""
    try:
        # Start the build process
        process = await asyncio.create_subprocess_shell(
            build_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd="../",  # Run from HueSurf root directory
        )

        bot.build_process = process
        bot.is_streaming = True
        bot.build_status = "Building"
        bot.progress_percentage = 0

        # Create initial message
        initial_embed = create_build_embed(
            "Starting", 0, ["🚀 Starting build process..."]
        )
        await interaction.edit_original_response(embed=initial_embed)

        # Stream output
        while True:
            line_bytes = await process.stdout.readline()
            if not line_bytes:
                break

            line = line_bytes.decode('utf-8', errors='replace').strip()

            if line:
                bot.log_buffer.append(line)

                # Try to extract progress
                progress = extract_progress_from_line(line)
                if progress is not None:
                    bot.progress_percentage = min(progress, 100)

                # Update Discord message every few seconds or on significant changes
                current_time = time.time()
                if (
                    not hasattr(bot, "_last_update_time")
                    or current_time - bot._last_update_time > 3
                    or progress is not None
                ):
                    bot._last_update_time = current_time

                    try:
                        embed = create_build_embed(
                            bot.build_status, bot.progress_percentage, bot.log_buffer
                        )
                        await bot.build_message.edit(embed=embed)
                    except discord.NotFound:
                        # Message was deleted, stop streaming
                        logger.warning("Build message was deleted, stopping stream")
                        process.terminate()
                        break
                    except Exception as e:
                        logger.error(f"Error updating message: {e}")

        # Process finished
        return_code = await process.wait()

        if return_code == 0:
            bot.build_status = "Complete"
            bot.progress_percentage = 100
            bot.log_buffer.append("✅ Build completed successfully!")
        else:
            bot.build_status = "Failed"
            bot.log_buffer.append(f"❌ Build failed with exit code {return_code}")

        # Final update
        final_embed = create_build_embed(
            bot.build_status, bot.progress_percentage, bot.log_buffer
        )
        await bot.build_message.edit(embed=final_embed)

    except Exception as e:
        logger.error(f"Error in build stream: {e}")
        bot.build_status = "Error"
        bot.log_buffer.append(f"❌ Stream error: {str(e)}")

        error_embed = create_build_embed(
            "Error", bot.progress_percentage, bot.log_buffer
        )
        try:
            await bot.build_message.edit(embed=error_embed)
        except:
            pass

    finally:
        bot.is_streaming = False
        bot.build_process = None


@bot.tree.command(
    name="buildprog", description="Start streaming HueSurf build progress"
)
@app_commands.describe(
    command="Build command to execute (default: scripts/build.sh)",
    log_file="Optional log file to monitor instead of command output",
)
async def build_progress_command(
    interaction: discord.Interaction,
    command: str = "scripts/build.sh",
    log_file: str = None,
):
    """Handle /buildprog command"""

    # Check if already streaming
    if bot.is_streaming:
        await interaction.response.send_message(
            "❌ Build stream is already active! Use `/buildstop` to stop the current stream.",
            ephemeral=True,
        )
        return

    # Validate build command/file exists
    if log_file:
        log_path = f"../{log_file}"
        if not os.path.exists(log_path):
            await interaction.response.send_message(
                f"❌ Log file not found: {log_file}", ephemeral=True
            )
            return
        build_command = f"tail -f {log_file}"
    else:
        script_path = f"../{command}"
        if not os.path.exists(script_path):
            await interaction.response.send_message(
                f"❌ Build script not found: {command}\n"
                f"Make sure the script exists in the HueSurf directory.",
                ephemeral=True,
            )
            return
        build_command = command

    # Set up tracking
    bot.build_channel = interaction.channel
    bot.log_buffer.clear()

    # Send initial response
    await interaction.response.send_message("🚀 Starting build stream...")
    bot.build_message = await interaction.original_response()

    # Start streaming in background
    asyncio.create_task(stream_build_process(interaction, build_command))


@bot.tree.command(name="buildstop", description="Stop current build stream")
async def build_stop_command(interaction: discord.Interaction):
    """Stop the current build stream"""

    if not bot.is_streaming:
        await interaction.response.send_message(
            "❌ No build stream is currently active.", ephemeral=True
        )
        return

    # Stop the build process
    if bot.build_process:
        bot.build_process.terminate()
        bot.build_process = None

    bot.is_streaming = False
    bot.build_status = "Stopped"
    bot.log_buffer.append("🛑 Build stream stopped by user")

    # Update message
    if bot.build_message:
        try:
            stopped_embed = create_build_embed(
                "Stopped", bot.progress_percentage, bot.log_buffer
            )
            await bot.build_message.edit(embed=stopped_embed)
        except:
            pass

    await interaction.response.send_message("✅ Build stream stopped.", ephemeral=True)


@bot.tree.command(name="buildstatus", description="Show current build stream status")
async def build_status_command(interaction: discord.Interaction):
    """Show current build status"""

    embed = discord.Embed(
        title="📊 Build Stream Status",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow(),
    )

    if bot.is_streaming:
        embed.add_field(name="Status", value="🟢 Active Stream", inline=True)
        embed.add_field(
            name="Progress", value=f"{bot.progress_percentage}%", inline=True
        )
        embed.add_field(name="Build Status", value=bot.build_status, inline=True)
    else:
        embed.add_field(name="Status", value="🔴 No Active Stream", inline=True)
        embed.add_field(name="Last Status", value=bot.build_status, inline=True)
        embed.add_field(
            name="Last Progress", value=f"{bot.progress_percentage}%", inline=True
        )

    embed.set_footer(text="Use /buildprog to start streaming")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands

    logger.error(f"Command error: {error}")


def main():
    """Main function to run the bot"""
    # Get Discord token from environment
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your Discord bot token:")
        logger.error("DISCORD_TOKEN=your_bot_token_here")
        return

    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Failed to login to Discord. Check your token!")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
