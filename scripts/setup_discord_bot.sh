#!/bin/bash

# HueSurf Discord Build Bot Setup Script
# This script helps set up the Discord bot for real-time build streaming

set -e

echo "🛠️  HueSurf Discord Build Bot Setup"
echo "===================================="

# Check if we're in the correct directory
if [ ! -f "discord_build_bot.py" ]; then
    echo "❌ Error: discord_build_bot.py not found!"
    echo "Please run this script from the HueSurf/scripts directory"
    exit 1
fi

# Check Python installation
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"

# Check pip installation
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Install Discord bot requirements
echo "📦 Installing Discord bot dependencies..."
if [ -f "requirements_discord.txt" ]; then
    pip3 install -r requirements_discord.txt
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  requirements_discord.txt not found, installing manually..."
    pip3 install discord.py python-dotenv
fi

# Check for .env file
echo "🔐 Checking environment configuration..."
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    if [ ! -f "../.env" ]; then
        echo "❌ Could not find .env template. Please create ../env file manually."
        echo "Add the following line to your .env file:"
        echo "DISCORD_TOKEN=your_discord_bot_token_here"
    fi
else
    echo "✅ Found .env file"
fi

# Make bot script executable
echo "🔧 Making bot script executable..."
chmod +x discord_build_bot.py

# Create systemd service file (optional)
echo "🔄 Would you like to create a systemd service file? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    SERVICE_FILE="huesurf-discord-bot.service"
    SCRIPT_PATH=$(realpath discord_build_bot.py)
    WORK_DIR=$(dirname "$SCRIPT_PATH")

    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=HueSurf Discord Build Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$WORK_DIR
Environment=PYTHONPATH=$WORK_DIR
ExecStart=/usr/bin/python3 $SCRIPT_PATH
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Created $SERVICE_FILE"
    echo "To install as a system service:"
    echo "  sudo cp $SERVICE_FILE /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable huesurf-discord-bot"
    echo "  sudo systemctl start huesurf-discord-bot"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://discord.com/developers/applications"
echo "2. Create a new application or select an existing one"
echo "3. Go to the 'Bot' section and create a bot"
echo "4. Copy the bot token"
echo "5. Edit ../env and replace 'your_discord_bot_token_here' with your actual token"
echo "6. Invite the bot to your Discord server with the following permissions:"
echo "   - Send Messages"
echo "   - Use Slash Commands"
echo "   - Embed Links"
echo "7. Run the bot with: python3 discord_build_bot.py"
echo ""
echo "🔗 Bot invite URL (replace CLIENT_ID with your application's client ID):"
echo "https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=2147483648&scope=bot%20applications.commands"
echo ""
echo "💡 Usage:"
echo "  /buildprog [command]       - Start streaming build progress"
echo "  /buildstop                 - Stop current build stream"
echo "  /buildstatus               - Show current stream status"
echo ""
echo "Happy building! 🚀"
