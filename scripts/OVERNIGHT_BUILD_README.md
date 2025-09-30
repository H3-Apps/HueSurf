# 🌙 HueSurf Overnight Build System

Sleep peacefully while your MacBook builds HueSurf browser overnight! This system prevents your Mac from sleeping and manages the entire build process while you rest.

## 🚀 Quick Start

### The Easy Way (Recommended)
```bash
cd HueSurf/scripts
./bedtime_build.sh --full
```

### The Manual Way
```bash
cd HueSurf/scripts
python3 overnight_build.py --discord --notify
```

## 🎯 What It Does

- **🔋 Prevents Sleep**: Uses macOS `caffeinate` to keep your MacBook awake during builds
- **🛠️ Runs Build**: Executes HueSurf build process with full logging
- **🤖 Discord Integration**: Optional real-time build updates in Discord
- **📱 Notifications**: macOS notifications for build start/completion
- **📝 Complete Logging**: Everything logged to `overnight_build.log`
- **🧹 Auto Cleanup**: Restores sleep settings when done
- **⚡ Smart Management**: Handles interruptions and errors gracefully

## 📋 Prerequisites

- **macOS**: Required for sleep prevention (`caffeinate`)
- **Python 3.8+**: For the build management system
- **HueSurf Project**: Must be run from the HueSurf/scripts directory
- **Build Dependencies**: All HueSurf build requirements installed

### Optional
- **Discord Bot**: For real-time build streaming (requires `.env` setup)
- **Battery**: Recommended for long builds (or keep plugged in)

## 🛠️ Available Scripts

### 1. `bedtime_build.sh` - The Simple Way

Perfect for before bedtime! Just run and go to sleep.

**Basic Usage:**
```bash
./bedtime_build.sh                 # Standard overnight build
./bedtime_build.sh --with-discord  # With Discord notifications
./bedtime_build.sh --fast-test     # 30-second test (for testing)
./bedtime_build.sh --full          # All features enabled
```

**Options:**
- `--with-discord`, `-d`: Enable Discord bot notifications
- `--fast-test`, `-f`: Run quick test build (30 seconds)
- `--no-notifications`, `-n`: Disable system notifications
- `--full`: Enable all features (Discord + notifications)
- `--help`, `-h`: Show help message

### 2. `overnight_build.py` - The Advanced Way

Full control over build process and options.

**Basic Usage:**
```bash
python3 overnight_build.py --discord --notify
```

**Options:**
- `--command`, `-c`: Custom build command (default: `scripts/build.sh`)
- `--log-file`, `-l`: Custom log file path (default: `overnight_build.log`)
- `--discord`, `-d`: Start Discord bot for real-time updates
- `--notify`, `-n`: Send macOS system notifications

## 💡 Usage Examples

### Before Bed (Most Common)
```bash
# Simple overnight build
./bedtime_build.sh

# With Discord updates so you can check progress from your phone
./bedtime_build.sh --with-discord

# Full featured build
./bedtime_build.sh --full
```

### Testing the System
```bash
# Quick 30-second test to verify everything works
./bedtime_build.sh --fast-test

# Test with Discord integration
./bedtime_build.sh --fast-test --with-discord
```

### Custom Builds
```bash
# Custom build command
python3 overnight_build.py --command "scripts/demo-build.sh"

# Monitor existing log file
python3 overnight_build.py --command "tail -f build.log"

# Custom log location
python3 overnight_build.py --log-file "logs/my_build.log"
```

## 🤖 Discord Integration

The overnight build system integrates with the HueSurf Discord bot to provide real-time updates.

### Setup Discord (Optional)
1. Set up the Discord bot (see `DISCORD_BOT_README.md`)
2. Configure your Discord token in `HueSurf/.env`
3. Use `--discord` flag when building

### What You'll See in Discord
- Real-time console output streaming
- Progress bars and percentage completion
- Build status updates (Building → Complete/Failed)
- Automatic progress detection from build logs

### Discord Commands During Build
- `/buildstatus` - Check current build progress
- `/buildstop` - Stop the build remotely
- The bot automatically updates the same message throughout the build

## 📊 Build Monitoring

### Log Files
- **Primary Log**: `overnight_build.log` - Complete build output and system messages
- **Build Summary**: `build_summary_YYYYMMDD_HHMMSS.json` - JSON summary of build results
- **Discord Bot Log**: Separate Discord bot logging (if enabled)

### System Notifications
macOS notifications will alert you:
- **Build Started**: When overnight build begins
- **Build Complete**: Success/failure with duration
- **Build Interrupted**: If build is stopped early

### Progress Tracking
The system automatically detects progress from:
- Direct percentages: `45%`
- Build ratios: `[1234/2500]`
- Progress indicators: `Progress: 45%`
- Build status: `Building chrome... 45%`

## ⚠️ Important Notes

### Battery Considerations
- **Long Builds**: Plug in your MacBook for overnight builds
- **Battery Warning**: Script warns if battery < 20%
- **Power Management**: `caffeinate` prevents sleep but uses power

### Laptop Lid Behavior
- **Safe to Close**: You can close your laptop lid during build
- **Display Sleep**: `caffeinate -d` prevents display sleep
- **System Sleep**: `caffeinate -i` prevents idle sleep
- **Network**: Wi-Fi stays active with lid closed

### Build Safety
- **Graceful Shutdown**: Ctrl+C stops build cleanly
- **Process Management**: All processes are properly terminated
- **Sleep Restoration**: System sleep settings always restored
- **Error Handling**: Robust error handling and recovery

## 🔧 Troubleshooting

### Common Issues

**"caffeinate command not found"**
- This should never happen on macOS
- Verify you're running on macOS: `uname -a`

**"Build script not found"**
- Ensure you're in the `HueSurf/scripts` directory
- Check that your build script exists: `ls -la ../scripts/build.sh`
- Verify script permissions: `chmod +x ../scripts/build.sh`

**"Discord bot failed to start"**
- Check `.env` file exists: `ls -la ../.env`
- Verify Discord token is set correctly
- Ensure Discord bot dependencies installed: `pip3 install -r requirements_discord.txt`

**"Build interrupted"**
- Check log file for details: `tail -50 overnight_build.log`
- Verify sufficient disk space: `df -h`
- Check for system updates or restarts

### Debug Mode
Enable verbose logging:
```bash
python3 overnight_build.py --discord --notify --log-file debug_build.log
```

Check system processes:
```bash
# See if caffeinate is running
ps aux | grep caffeinate

# Check build process
ps aux | grep build

# Monitor system sleep settings
pmset -g assertions
```

### Log Analysis
```bash
# View recent logs
tail -100 overnight_build.log

# Search for errors
grep -i error overnight_build.log

# Check build progress
grep -i "progress\|%" overnight_build.log

# View build summary
cat build_summary_*.json | jq .
```

## 📂 File Structure

```
HueSurf/scripts/
├── overnight_build.py         # Main overnight build system
├── bedtime_build.sh          # Simple wrapper script
├── discord_build_bot.py      # Discord bot (optional)
├── example-build.sh          # Test build script
├── OVERNIGHT_BUILD_README.md # This file
└── overnight_build.log       # Build logs (generated)

HueSurf/
└── .env                      # Discord token (for bot)
```

## ⏱️ Build Time Estimates

### Typical HueSurf Build Times
- **Full Release Build**: 2-4 hours (depends on hardware)
- **Debug Build**: 1-2 hours
- **Incremental Build**: 15-30 minutes
- **Clean Build**: 3-6 hours

### Hardware Impact
- **M1/M2 Mac**: Faster builds, better battery efficiency
- **Intel Mac**: Longer builds, more heat/power usage
- **RAM**: 16GB+ recommended for parallel compilation
- **SSD**: Significantly faster than HDD

## 🎯 Best Practices

### Before Starting Overnight Build
1. **Plug In**: Connect to power for long builds
2. **Close Apps**: Quit unnecessary applications
3. **Free Space**: Ensure 50GB+ free disk space
4. **Test First**: Run `--fast-test` to verify setup
5. **Check Network**: Stable internet for dependencies

### During Build
- **Lid Closed**: Safe to close laptop and sleep
- **Remote Monitoring**: Use Discord bot to check progress
- **Phone Notifications**: Enable to get completion alerts

### After Build
- **Check Logs**: Review `overnight_build.log` for any issues
- **Test Binary**: Verify build output works correctly
- **Clean Up**: Remove intermediate build files if needed

## 💡 Tips & Tricks

### Save Battery
```bash
# Reduce display brightness (if you're staying up)
brightness 0.1

# Enable low power mode before building
sudo pmset -a lowpowermode 1
```

### Multiple Builds
```bash
# Different log files for different builds
python3 overnight_build.py --log-file "release_build.log" --command "scripts/build.sh --release"
python3 overnight_build.py --log-file "debug_build.log" --command "scripts/build.sh --debug"
```

### Scheduled Builds
```bash
# Use cron for automated nightly builds (advanced)
# Add to crontab: 0 23 * * * cd /path/to/HueSurf/scripts && ./bedtime_build.sh
```

## 🔗 Related Documentation

- **[Discord Bot README](DISCORD_BOT_README.md)**: Discord integration setup
- **[Main Build Guide](../BUILD.md)**: HueSurf build instructions
- **[Build Scripts](../scripts/)**: Available build commands

---

**Sweet dreams and happy building! 🌙✨**

*Your MacBook will work hard while you rest, and you'll wake up to a fresh HueSurf browser build!*