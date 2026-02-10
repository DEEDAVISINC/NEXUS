#!/bin/bash
# Setup daily automated bid management
# Runs every morning at 7 AM automatically

SCRIPT_DIR="/Users/deedavis/NEXUS BACKEND"
PLIST_FILE="$HOME/Library/LaunchAgents/com.deedavis.nexus.bidmanager.plist"

echo "🤖 Setting up NEXUS Daily Automation..."
echo ""

# Create LaunchAgent plist file
cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.deedavis.nexus.bidmanager</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_DIR/auto_bid_manager.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>7</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/bid_manager_output.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/bid_manager_error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Load the launch agent
launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"

echo "✅ Automation setup complete!"
echo ""
echo "📅 NEXUS Bid Manager will run automatically:"
echo "   - Every morning at 7:00 AM"
echo "   - Generates TODAY_AGENDA.md"
echo "   - Updates calendar events"
echo "   - Asks status questions"
echo "   - Sends notification"
echo ""
echo "📂 Logs saved to: $SCRIPT_DIR/logs/"
echo ""
echo "🎯 To run manually anytime:"
echo "   python3 auto_bid_manager.py"
echo ""
echo "🔧 To stop automation:"
echo "   launchctl unload $PLIST_FILE"
echo ""
