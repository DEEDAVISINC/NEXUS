#!/bin/bash
# Setup automatic daily bid manager

echo "🤖 Setting up NEXUS Automated Bid Manager"
echo ""

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/adaptive_bid_system.py"

echo "📍 Script location: $SCRIPT_PATH"
echo ""

# Create launch agent for macOS (runs daily at 7 AM)
PLIST_PATH="$HOME/Library/LaunchAgents/com.deedavis.nexus.bidmanager.plist"

echo "📝 Creating launch agent..."

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.deedavis.nexus.bidmanager</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_PATH</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$(dirname "$SCRIPT_PATH")</string>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/nexus_bid_manager.log</string>
    
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/nexus_bid_manager_error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo "✅ Launch agent created: $PLIST_PATH"
echo ""

# Load the launch agent
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "✅ Launch agent loaded"
echo ""
echo "🎯 SETUP COMPLETE!"
echo ""
echo "The bid manager will now run automatically every morning at 7:00 AM"
echo ""
echo "You'll get:"
echo "  📅 Updated TODAY_AGENDA.md"
echo "  🤔 BID_STATUS_QUESTIONS.md (if needed)"
echo "  📆 Fresh calendar files"
echo "  🔔 Desktop notification"
echo ""
echo "To run manually: python3 auto_bid_manager.py"
echo "To check logs: tail -f ~/Library/Logs/nexus_bid_manager.log"
echo ""
