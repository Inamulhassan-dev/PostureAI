# 🏋️ PostureAI — Intelligent Exercise Posture Analysis System

> Real-time AI-powered exercise posture analysis and correction using Computer Vision, MediaPipe, and Machine Learning.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)](https://flask.palletsprojects.com)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-orange?logo=google)](https://mediapipe.dev)
[![CI](https://github.com/Inamulhassan-dev/PostureAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Inamulhassan-dev/PostureAI/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📸 Features

- **🎯 Real-time Pose Detection** — MediaPipe tracks 33 body landmarks at 30 FPS
- **📐 Joint Angle Analysis** — Precise biomechanical angle computation for every rep
- **💬 Instant Feedback** — Color-coded overlay shows correct / incorrect posture live
- **🔢 Auto Rep Counter** — Counts repetitions automatically from movement patterns
- **📊 Form Score** — Real-time percentage score for exercise form quality
- **🤖 ML Classification** — Trained Random Forest / SVM models for posture classification
- **🌐 Web Interface** — Beautiful browser-based dashboard with live video
- **🖥️ Desktop Mode** — Standalone OpenCV window for power users

---

## 🏃 Supported Exercises

| Exercise | Key Joints Analyzed | Feedback |
|---|---|---|
| **Squat** | Knee angle, Hip angle, Back straightness | Depth, back rounding, knee symmetry |
| **Push-up** | Elbow angle, Body alignment | Depth, hip sag/pike, form |
| **Bicep Curl** | Elbow angle, Shoulder movement | Swing detection, full ROM |
| **Lunge** | Front knee, Torso angle | Knee tracking, torso upright |
| **Shoulder Press** | Elbow extension, Shoulder symmetry | Full extension, shoulder alignment |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9 – 3.12** installed ([download here](https://python.org/downloads/))
  - Windows: ✅ Check **"Add Python to PATH"** during installation
  - macOS: use `brew install python` or the official installer
  - Linux: use your package manager, e.g. `sudo apt install python3 python3-venv`
- **Webcam** connected to your computer
- **Git** installed

### 1 · Clone

```bash
git clone https://github.com/Inamulhassan-dev/PostureAI.git
cd PostureAI
```

### 2 · Launch

| Platform | Command |
|---|---|
| **Windows** | Double-click `START.bat` **or** run it in a terminal |
| **macOS / Linux** | `bash start.sh` |

The launcher will automatically:
1. ✅ Create a Python virtual environment
2. ✅ Install all packages from `requirements.txt`
3. ✅ Train ML models (first run only, ~30 s)
4. ✅ Run a system diagnostic
5. ✅ Open your browser to **http://localhost:5000**

---

## 📁 Project Structure

```
PostureAI/
├── config.py                    # Central configuration & thresholds
├── main_app.py                  # Standalone OpenCV desktop app
├── web_app.py                   # Flask web application
├── data_collector.py            # Training data collection tool
├── train_model.py               # ML model training pipeline
├── check_system.py              # Full system diagnostic (13 checks)
├── test_system.py               # Automated test suite
├── verify_setup.py              # Quick dependency check
├── requirements.txt             # Python dependencies
├── START.bat                    # One-click launcher (auto-setup)
├── STOP.bat                     # Graceful shutdown
├── run.bat                      # Interactive menu
│
├── utils/
│   ├── pose_detector.py         # MediaPipe Pose wrapper
│   ├── angle_calculator.py      # Joint angle mathematics
│   └── feedback_generator.py    # Visual & text feedback engine
│
├── exercises/
│   ├── squat_analyzer.py        # Squat posture analysis
│   ├── pushup_analyzer.py       # Push-up posture analysis
│   ├── bicep_curl_analyzer.py   # Bicep curl posture analysis
│   ├── lunge_analyzer.py        # Lunge posture analysis
│   └── shoulder_press_analyzer.py # Shoulder press analysis
│
├── models/                      # Pre-trained ML model files (.pkl)
│
├── data/
│   ├── collected/               # Raw pose data CSVs
│   └── processed/               # Synthetic training data
│
├── templates/                   # Flask HTML templates
│   ├── index.html               # Home page with exercise selection
│   ├── exercise.html            # Live analysis dashboard
│   └── history.html             # Workout history (coming soon)
│
└── static/
    ├── css/style.css             # Premium dark theme UI
    └── js/main.js                # Dashboard real-time updates
```

---

## 🔧 Manual Setup

If you prefer to set things up yourself:

```bash
# ── 1. Create & activate a virtual environment ──────────────────────────────
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# ── 2. Install dependencies ──────────────────────────────────────────────────
pip install -r requirements.txt

# ── 3. Train ML models (one-time, ~30 seconds) ──────────────────────────────
python train_model.py
# Select option 2 → "Train all exercises"

# ── 4. Verify the installation ───────────────────────────────────────────────
python check_system.py

# ── 5. Run ───────────────────────────────────────────────────────────────────
python web_app.py          # web interface → http://localhost:5000
# or
python main_app.py         # standalone OpenCV desktop window
```

### GPU / CPU note

MediaPipe runs on **CPU by default** — no GPU or CUDA setup is required.
If you have a machine with a supported GPU and want to experiment with
`model_complexity=2` (heavy model), see the `MODEL_COMPLEXITY` setting in
`config.py`.

---

## 🖥️ Desktop App (OpenCV)

```bash
python main_app.py
```

### Keyboard Controls

| Key | Action |
|:---:|---|
| `1` | Switch to Squat |
| `2` | Switch to Push-up |
| `3` | Switch to Bicep Curl |
| `4` | Switch to Lunge |
| `5` | Switch to Shoulder Press |
| `R` | Reset rep counter |
| `Q` / `ESC` | Quit |

---

## 🧪 System Tools

| Script | Purpose |
|---|---|
| `START.bat` | **One-click launcher** — auto-setup + run |
| `STOP.bat` | Gracefully stop the running app |
| `run.bat` | Interactive menu for all tools |
| `check_system.py` | Full diagnostic (13 automated checks) |
| `test_system.py` | Run automated test suite |
| `data_collector.py` | Collect training data with webcam |
| `train_model.py` | Train/retrain ML models |

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Pose Detection** | MediaPipe Pose (33 landmarks) |
| **Computer Vision** | OpenCV |
| **Web Framework** | Flask |
| **ML Models** | Scikit-learn (Random Forest, SVM, Gradient Boosting) |
| **Data Processing** | NumPy, Pandas |
| **Visualization** | Matplotlib, Seaborn |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Voice Feedback** | pyttsx3 (optional) |

---

## 📋 System Requirements

| | Minimum |
|---|---|
| **OS** | Windows 10/11, macOS 12+, Ubuntu 20.04+ |
| **Python** | 3.9 – 3.12 (3.10 recommended) |
| **RAM** | 4 GB |
| **Webcam** | Any USB or built-in camera |
| **Browser** | Chrome, Firefox, or Edge (for web app) |

> **Note:** No GPU or CUDA is required. MediaPipe performs all pose estimation on CPU.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) by Google for pose estimation
- [OpenCV](https://opencv.org/) for computer vision
- [Scikit-learn](https://scikit-learn.org/) for machine learning
- [Flask](https://flask.palletsprojects.com/) for the web framework

---

<p align="center">
  <b>Built with ❤️ for fitness enthusiasts who want perfect form</b><br>
  <i>Intelligent Computer Vision System for Exercise Posture Analysis and Correction</i>
</p>
