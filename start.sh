#!/usr/bin/env bash
# start.sh — PostureAI launcher for macOS and Linux
# Usage:  bash start.sh
set -e

BOLD="\033[1m"
CYAN="\033[96m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
DIM="\033[2m"
RESET="\033[0m"

BASE="$(cd "$(dirname "$0")" && pwd)"

echo
echo -e "${CYAN}${BOLD}+==============================================================+"
echo -e "|     PostureAI - Exercise Posture Analysis                    |"
echo -e "|     Intelligent Computer Vision System  |  Launcher          |"
echo -e "+==============================================================+${RESET}"
echo

# ── Step 1 · Python ──────────────────────────────────────────────────────────
echo -e "${CYAN}${BOLD}  [1/5]  Checking Python installation...${RESET}"
if ! command -v python3 &>/dev/null; then
    echo -e "  ${RED}[!!]  python3 not found!${RESET}"
    echo -e "  ${YELLOW}  ->  macOS:  brew install python${RESET}"
    echo -e "  ${YELLOW}  ->  Linux:  sudo apt install python3 python3-venv${RESET}"
    exit 1
fi
PYTHON_BIN="python3"
PY_VER=$("$PYTHON_BIN" --version 2>&1)
echo -e "  ${GREEN}[OK]${RESET}  $PY_VER detected"
echo

# ── Step 2 · Virtual environment ─────────────────────────────────────────────
echo -e "${CYAN}${BOLD}  [2/5]  Setting up virtual environment...${RESET}"
VENV="$BASE/venv"
if [ ! -f "$VENV/bin/python" ]; then
    echo -e "  ${YELLOW}[??]  venv not found — creating now...${RESET}"
    "$PYTHON_BIN" -m venv "$VENV"
    echo -e "  ${GREEN}[OK]${RESET}  Virtual environment created."
else
    echo -e "  ${GREEN}[OK]${RESET}  Virtual environment found."
fi
"$VENV/bin/python" -m pip install --upgrade pip --quiet 2>/dev/null
echo

# ── Step 3 · Packages ────────────────────────────────────────────────────────
echo -e "${CYAN}${BOLD}  [3/5]  Verifying pip packages...${RESET}"
if ! "$VENV/bin/python" -c \
    "import cv2,mediapipe,flask,sklearn,numpy,pandas,joblib,matplotlib,seaborn,PIL" \
    2>/dev/null; then
    echo -e "  ${YELLOW}[??]  Some packages missing — installing from requirements.txt...${RESET}"
    echo -e "  ${DIM}       (this may take a few minutes on first run)${RESET}"
    "$VENV/bin/pip" install -r "$BASE/requirements.txt" --quiet
    echo -e "  ${GREEN}[OK]${RESET}  All packages installed."
else
    echo -e "  ${GREEN}[OK]${RESET}  All core packages present."
fi
echo

# ── Step 4 · ML models ───────────────────────────────────────────────────────
echo -e "${CYAN}${BOLD}  [4/5]  Checking ML models...${RESET}"
MODELS_OK=1
for EX in squat pushup bicep_curl lunge shoulder_press; do
    if [ ! -f "$BASE/models/${EX}_model.pkl" ]; then
        MODELS_OK=0
        break
    fi
done

if [ "$MODELS_OK" -eq 0 ]; then
    echo -e "  ${YELLOW}[??]  Some ML models missing — auto-training now...${RESET}"
    echo -e "  ${DIM}       (one-time process, ~30 seconds)${RESET}"
    cd "$BASE"
    "$VENV/bin/python" -c \
        "from train_model import PostureModelTrainer; t=PostureModelTrainer(); t.train_all_exercises()"
    echo -e "  ${GREEN}[OK]${RESET}  All ML models trained."
else
    echo -e "  ${GREEN}[OK]${RESET}  All 5 ML models present."
fi
echo

# ── Step 5 · Diagnostic ──────────────────────────────────────────────────────
echo -e "${CYAN}${BOLD}  [5/5]  Running system diagnostic...${RESET}"
cd "$BASE"
"$VENV/bin/python" check_system.py
DIAG_CODE=$?
if [ "$DIAG_CODE" -ne 0 ]; then
    echo
    echo -e "  ${RED}${BOLD}  Diagnostic found issues. Fix them then re-run start.sh${RESET}"
    exit 1
fi

# ── Launch ───────────────────────────────────────────────────────────────────
echo
echo -e "${GREEN}${BOLD}+==============================================================+"
echo -e "|  [OK]  All checks passed! Launching PostureAI...             |"
echo -e "+==============================================================+${RESET}"
echo
echo -e "  ${CYAN}  Web App URL  :  http://localhost:5000${RESET}"
echo -e "  ${DIM}  Press Ctrl+C to stop${RESET}"
echo

# Open browser after 3 seconds (best-effort)
(sleep 3 && (open "http://localhost:5000" 2>/dev/null || xdg-open "http://localhost:5000" 2>/dev/null || true)) &

"$VENV/bin/python" "$BASE/web_app.py"
