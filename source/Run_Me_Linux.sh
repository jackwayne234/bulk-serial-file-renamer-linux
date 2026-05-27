#!/bin/bash
# PHOTO BOOSTER - PRO LINUX LAUNCHER
# Optimized for Gumroad Customers

# Move to the directory where this script is located
cd "$(dirname "$0")"

# --- 1. Terminal Handling + Logging ---
LOG_FILE="${TMPDIR:-/tmp}/photo_booster_launcher.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# One-click package mode: do not force-open terminal windows.
# All output is written to $LOG_FILE for troubleshooting.

echo "========================================"
echo "   PHOTO BOOSTER - PRO LINUX"
echo "========================================"
echo ""

# --- 2. Preflight Checks ---

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed."
    echo "Please install it: sudo apt update && sudo apt install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Tkinter (The most common Linux Python issue)
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "❌ ERROR: Python Tkinter support is missing."
    echo "This is required for the app interface."
    echo "Please install it: sudo apt update && sudo apt install python3-tk"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# --- 3. Preferred Path: Python Source Mode ---
# Source mode is the most patchable/resilient path across diverse Linux systems.
# AppImage is used as a fallback if source mode cannot start.

# --- 4. Python Source Mode ---

# Setup Virtual Environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Setting up your private app environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ FAILED to create virtual environment."
        echo "You might need to install the venv tool: sudo apt update && sudo apt install python3-venv"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Install/Update requirements
echo "🛠️  Checking requirements (this may take a moment on first run)..."
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt

# Launch the App
echo "🚀 Launching Photo Booster..."
./venv/bin/python app.py "$@"
LAUNCH_EXIT=$?

if [ $LAUNCH_EXIT -ne 0 ]; then
    echo ""
    echo "⚠️  Python source mode exited with code $LAUNCH_EXIT."

    if [ -f "PhotoBooster-x86_64.AppImage" ]; then
        echo "📦 Trying AppImage fallback..."
        chmod +x "PhotoBooster-x86_64.AppImage" 2>/dev/null || true
        export APPIMAGE_EXTRACT_AND_RUN=1

        APPIMAGE_LOG="/tmp/photo_booster_appimage_fallback.log"
        ./PhotoBooster-x86_64.AppImage "$@" > "$APPIMAGE_LOG" 2>&1
        APP_EXIT=$?

        if [ $APP_EXIT -eq 0 ]; then
            exit 0
        else
            echo "❌ AppImage fallback also failed (Code: $APP_EXIT)."
            echo "Last 20 lines from AppImage log:"
            tail -n 20 "$APPIMAGE_LOG"
        fi
    fi

    echo "Please copy the error above if you need support."
    echo ""
    read -p "Press Enter to exit..."
    exit $LAUNCH_EXIT
fi

