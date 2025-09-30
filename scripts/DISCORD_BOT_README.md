# HueSurf Discord Build Bot

A Discord bot that streams real-time console output and build progress for HueSurf browser builds.

## 🚀 Features

- **Live Console Streaming**: Stream real-time build console output to Discord
- **Automatic Progress Detection**: Automatically extracts progress from build logs
- **Slash Commands**: Modern Discord slash command interface
- **Live Message Updates**: Updates the same message with streaming output
- **Visual Progress Bars**: ASCII progress bars with auto-detected percentage
- **Process Management**: Start, stop, and monitor build processes
- **Error Handling**: Robust error handling and logging

## 📋 Prerequisites

- Python 3.8 or later
- Discord account and server with admin permissions
- Discord Developer Application and Bot Token

## 🛠️ Quick Setup

### 1. Run the Setup Script

```bash
cd HueSurf/scripts
./setup_discord_bot.sh
```

This will:
- Check Python installation
- Install required dependencies
- Create service files (optional)
- Guide you through the setup process

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Install dependencies
pip3 install -r requirements_discord.txt

# Make the bot script executable
chmod +x discord_build_bot.py
```

## 🔐 Discord Bot Configuration

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "HueSurf Build Bot")
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot" if not already created
5. Copy the bot token (keep it secure!)

### 2. Configure Environment Variables

Edit the `.env` file in the HueSurf root directory:

```env
DISCORD_TOKEN=your_actual_discord_bot_token_here
LOG_LEVEL=INFO
```

### 3. Invite Bot to Server

Use this URL (replace `CLIENT_ID` with your application's client ID):

```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=2147483648&scope=bot%20applications.commands
```

**Required Permissions:**
- Send Messages
- Use Slash Commands
- Embed Links
- Read Message History

## 🎮 Usage

### Starting the Bot

```bash
cd HueSurf/scripts
python3 discord_build_bot.py
```

The bot will:
- Connect to Discord
- Sync slash commands
- Be ready to receive build updates

### Available Commands

#### `/buildprog [command] [log_file]`
Starts streaming real-time build progress and console output.

**Parameters:**
- `command` (optional): Build script to execute (default: `scripts/build.sh`)
- `log_file` (optional): Monitor existing log file instead of running command

**Examples:**
- `/buildprog` - Stream default build script output
- `/buildprog scripts/demo-build.sh` - Stream custom build script
- `/buildprog log_file:build.log` - Monitor existing log file

#### `/buildstop`
Stops the current build stream and terminates the process.

#### `/buildstatus`
Shows current build stream status and progress information.

## 📊 Real-time Build Display

The bot displays live build progress with streaming console output:

```
🛠️ HueSurf Browser Build Progress
Status: Building
Progress: 45%

Progress
████████████░░░░░░░░ 45%

🖥️ Console Output
[1234/2678] Compiling src/chrome/browser/ui/views/tabs/tab.cc
[1235/2678] Compiling src/chrome/browser/ui/views/tabs/tab_strip.cc
Building chrome... 45%
[1236/2678] Linking chrome executable
```

## 🔧 Integration with Build Scripts

### Method 1: Direct Script Execution (Recommended)

The bot can directly execute and stream your build scripts:

```bash
# Use Discord command to run your build script
/buildprog scripts/build.sh
```

The bot will automatically:
- Execute the build script
- Stream console output in real-time
- Extract progress percentages from output
- Update Discord with live progress

### Method 2: Log File Monitoring

Stream from existing log files during build:

```bash
# Start your build in background with logging
scripts/build.sh > build.log 2>&1 &

# Stream the log file to Discord
/buildprog log_file:build.log
```

### Method 3: Custom Build Scripts

Create build scripts with progress indicators that the bot can detect:

```bash
#!/bin/bash
# enhanced-build.sh

echo "Starting HueSurf build..."
echo "Progress: 0%"

# Step 1
echo "Configuring build environment..."
echo "Progress: 10%"

# Step 2  
echo "Compiling source files..."
echo "Progress: 50%"

# Step 3
echo "Linking executables..."
echo "Progress: 90%"

echo "Build complete!"
echo "Progress: 100%"
```

## 🚀 Running as a Service

### Using systemd (Linux)

The setup script can create a systemd service file:

```bash
sudo cp huesurf-discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable huesurf-discord-bot
sudo systemctl start huesurf-discord-bot
```

**Service Management:**
```bash
# Check status
sudo systemctl status huesurf-discord-bot

# View logs
sudo journalctl -u huesurf-discord-bot -f

# Restart service
sudo systemctl restart huesurf-discord-bot
```

### Using Screen/tmux (Alternative)

```bash
# Using screen
screen -S discord-bot python3 discord_build_bot.py

# Using tmux
tmux new-session -d -s discord-bot 'python3 discord_build_bot.py'
```

## 🐛 Troubleshooting

### Common Issues

**1. "DISCORD_TOKEN not found"**
- Check that `.env` file exists in the HueSurf root directory
- Verify the token is correctly set in the `.env` file
- Ensure no extra spaces around the token

**2. "Failed to sync commands"**
- Bot may not have proper permissions in the server
- Try re-inviting the bot with updated permissions
- Check Discord server settings for slash command permissions

**3. "Build stream already active"**
- Another build is currently streaming
- Use `/buildstop` to stop the current stream
- Wait for the current build to complete

**4. "Build script not found"**
- The specified build script doesn't exist
- Check the script path relative to HueSurf directory
- Ensure script has execute permissions

**5. Bot not responding to commands**
- Check bot is online in Discord
- Verify bot has "Use Slash Commands" permission
- Check server settings for application command permissions

### Debug Mode

Enable debug logging by setting in `.env`:

```env
LOG_LEVEL=DEBUG
```

### Log Files

Bot logs are output to console. To save to file:

```bash
python3 discord_build_bot.py > discord_bot.log 2>&1
```

## 🔧 Development

### File Structure

```
HueSurf/scripts/
├── discord_build_bot.py      # Main bot script
├── requirements_discord.txt  # Python dependencies
├── setup_discord_bot.sh      # Setup script
├── DISCORD_BOT_README.md     # This file
└── huesurf-discord-bot.service # Systemd service file (generated)

HueSurf/
└── .env                      # Environment variables
```

### Adding New Commands

To add new slash commands, create a function decorated with `@bot.tree.command`:

```python
@bot.tree.command(name="newcommand", description="Description here")
async def new_command(interaction: discord.Interaction, param: str):
    await interaction.response.send_message(f"Response: {param}")
```

### Customizing Embeds

Modify the `create_build_embed` function to change the appearance of build status messages.

## 📝 License

This Discord bot is part of the HueSurf project. See the main LICENSE file for details.

## 🤝 Contributing

1. Fork the HueSurf repository
2. Create a feature branch
3. Make your changes to the Discord bot
4. Test thoroughly
5. Submit a pull request

## 📞 Support

- **Issues**: Create an issue in the HueSurf repository
- **Discord**: Join the HueSurf Discord server
- **Documentation**: See the main HueSurf README.md

---

## 🔧 Progress Detection Patterns

The bot automatically detects progress from these common build output patterns:

- `45%` - Direct percentage
- `[1234/2500]` - Current/total format  
- `1234 of 2500` - X of Y format
- `Progress: 45%` - Explicit progress indicator
- `Building... 45%` - Build status with percentage

Add these patterns to your build scripts for automatic progress tracking.

**Happy Building! 🎉**