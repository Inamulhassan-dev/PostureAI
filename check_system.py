"""
check_system.py - Full System Diagnostic
Checks all files, folders, packages, models, camera, and features.
Exits with code 0 if everything OK, code 1 if something is missing.
"""
import sys
import os
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import importlib

# ─── ANSI Colors ────────────────────────────────────────────────────────────
os.system("")  # Enable ANSI on Windows
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
DIM    = "\033[2m"

# ASCII-safe symbols
OK_SYM   = "[OK]"
FAIL_SYM = "[!!]"
WARN_SYM = "[??]"
INFO_SYM = "[--]"

def banner():
    print(f"""
{CYAN}{BOLD}+==============================================================+
|    PostureAI - Full System Diagnostic                        |
|    Intelligent Computer Vision Exercise Posture System       |
+==============================================================+{RESET}
""")

def section(title):
    bar = "=" * (52 - len(title))
    print(f"\n{BLUE}{BOLD}---  {title}  {bar}{RESET}")

def ok(msg):    print(f"  {GREEN}{OK_SYM}{RESET}  {msg}")
def warn(msg):  print(f"  {YELLOW}{WARN_SYM}{RESET}  {msg}")
def fail(msg):  print(f"  {RED}{FAIL_SYM}{RESET}  {RED}{msg}{RESET}")
def info(msg):  print(f"  {CYAN}{INFO_SYM}{RESET}  {DIM}{msg}{RESET}")

# ─── Issue tracking ─────────────────────────────────────────────────────────
issues   = []
warnings = []

def add_issue(msg, fix=""):
    issues.append((msg, fix))
    fail(msg)
    if fix:
        print(f"        {YELLOW}-> FIX: {fix}{RESET}")

def add_warn(msg):
    warnings.append(msg)
    warn(msg)

# ════════════════════════════════════════════════════════════════════
# 1. PYTHON VERSION
# ════════════════════════════════════════════════════════════════════
def check_python():
    section("Python Version")
    v = sys.version_info
    ver_str = f"{v.major}.{v.minor}.{v.micro}"
    if v.major == 3 and v.minor >= 8:
        ok(f"Python {ver_str}  (required >= 3.8)")
    else:
        add_issue(
            f"Python {ver_str} is too old (need >= 3.8)",
            "Download from https://python.org and choose Python 3.10"
        )

# ════════════════════════════════════════════════════════════════════
# 2. VIRTUAL ENVIRONMENT
# ════════════════════════════════════════════════════════════════════
def check_venv():
    section("Virtual Environment")
    base       = os.path.dirname(os.path.abspath(__file__))
    venv_path  = os.path.join(base, "venv")

    # Support both Windows (Scripts/) and Unix (bin/) layouts
    if sys.platform == "win32":
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        py_path  = os.path.join(venv_path, "Scripts", "python.exe")
        activate_hint = r"venv\Scripts\activate"
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
        py_path  = os.path.join(venv_path, "bin", "python")
        activate_hint = "source venv/bin/activate"

    if os.path.isdir(venv_path):
        ok(f"venv/ folder exists")
    else:
        add_issue("venv/ not found", "Run:  python -m venv venv")
        return

    if os.path.isfile(pip_path):
        ok("pip inside venv")
    else:
        add_issue("pip missing inside venv", "Run:  python -m venv venv --clear")

    if os.path.isfile(py_path):
        ok("python inside venv")
    else:
        add_issue("python missing inside venv", "Run:  python -m venv venv --clear")

# ════════════════════════════════════════════════════════════════════
# 3. REQUIRED FOLDERS
# ════════════════════════════════════════════════════════════════════
REQUIRED_DIRS = [
    "utils", "exercises",
    "data", "data/collected", "data/processed",
    "models",
    "static", "static/css", "static/js",
    "templates",
]

def check_folders():
    section("Project Folders")
    base    = os.path.dirname(os.path.abspath(__file__))
    all_ok  = True
    for d in REQUIRED_DIRS:
        full = os.path.join(base, d.replace("/", os.sep))
        if os.path.isdir(full):
            ok(f"/{d}")
        else:
            add_issue(f"Folder missing: /{d}", f"Run:  mkdir {d}")
            all_ok = False
    if all_ok:
        info("All required directories present")

# ════════════════════════════════════════════════════════════════════
# 4. SOURCE FILES
# ════════════════════════════════════════════════════════════════════
REQUIRED_FILES = {
    "config.py":                            "Main configuration",
    "main_app.py":                          "Standalone OpenCV app",
    "web_app.py":                           "Flask web application",
    "data_collector.py":                    "Data collection tool",
    "train_model.py":                       "ML model trainer",
    "test_system.py":                       "System tests",
    "verify_setup.py":                      "Setup verifier",
    "check_system.py":                      "This diagnostic script",
    "requirements.txt":                     "Pip dependencies",
    "utils/__init__.py":                    "Utils package init",
    "utils/pose_detector.py":              "MediaPipe wrapper",
    "utils/angle_calculator.py":           "Angle calculations",
    "utils/feedback_generator.py":         "Feedback engine",
    "exercises/__init__.py":               "Exercises package init",
    "exercises/squat_analyzer.py":         "Squat analyzer",
    "exercises/pushup_analyzer.py":        "Pushup analyzer",
    "exercises/bicep_curl_analyzer.py":    "Bicep curl analyzer",
    "exercises/lunge_analyzer.py":         "Lunge analyzer",
    "exercises/shoulder_press_analyzer.py":"Shoulder press analyzer",
    "templates/index.html":                "Home page template",
    "templates/exercise.html":             "Exercise page template",
    "templates/history.html":              "History page template",
    "static/css/style.css":               "Stylesheet",
    "static/js/main.js":                  "Frontend JS",
}

def check_source_files():
    section("Source Files")
    base    = os.path.dirname(os.path.abspath(__file__))
    missing = 0
    for rel_path, description in REQUIRED_FILES.items():
        full = os.path.join(base, rel_path.replace("/", os.sep))
        if os.path.isfile(full):
            size = os.path.getsize(full)
            ok(f"{rel_path:<48}  ({size:,} bytes)")
        else:
            add_issue(f"Missing: {rel_path}  [{description}]",
                      "Re-run project setup to regenerate this file")
            missing += 1
    if missing == 0:
        info(f"All {len(REQUIRED_FILES)} source files present")

# ════════════════════════════════════════════════════════════════════
# 5. PIP PACKAGES
# ════════════════════════════════════════════════════════════════════
REQUIRED_PACKAGES = {
    "cv2":        ("opencv-python", "4.x"),
    "mediapipe":  ("mediapipe",     "0.10.x"),
    "numpy":      ("numpy",         "1.x"),
    "pandas":     ("pandas",        "2.x"),
    "sklearn":    ("scikit-learn",  "1.x"),
    "flask":      ("Flask",         "3.x"),
    "matplotlib": ("matplotlib",    "3.x"),
    "seaborn":    ("seaborn",       "0.12.x"),
    "joblib":     ("joblib",        "1.x"),
    "PIL":        ("Pillow",        "10.x"),
}
OPTIONAL_PACKAGES = {
    "pyttsx3": ("pyttsx3", "2.x  [voice feedback — optional]"),
}

def check_packages():
    section("Python Packages (pip)")
    # Build a cross-platform install hint once
    if sys.platform == "win32":
        pip_cmd = r"venv\Scripts\pip"
    else:
        pip_cmd = "venv/bin/pip"

    all_ok = True
    for import_name, (pip_name, version) in REQUIRED_PACKAGES.items():
        try:
            mod = importlib.import_module(import_name)
            ver = getattr(mod, "__version__", "?")
            ok(f"{pip_name:<22} {ver:<14}  (required {version})")
        except ImportError:
            add_issue(
                f"Package not installed: {pip_name}",
                f"Run:  {pip_cmd} install {pip_name}"
            )
            all_ok = False
    print()
    for import_name, (pip_name, version) in OPTIONAL_PACKAGES.items():
        try:
            importlib.import_module(import_name)
            ok(f"{pip_name:<22} installed  (optional: {version})")
        except ImportError:
            add_warn(f"Optional package missing: {pip_name}  -> {version}")
            info(f"  Install:  {pip_cmd} install {pip_name}")
    if all_ok:
        info("All required packages installed")

# ════════════════════════════════════════════════════════════════════
# 6. TRAINED ML MODELS
# ════════════════════════════════════════════════════════════════════
EXERCISES   = ["squat", "pushup", "bicep_curl", "lunge", "shoulder_press"]
MODEL_FILES = ["{}_model.pkl", "{}_label_encoder.pkl", "{}_features.pkl"]

def check_models():
    section("Trained ML Models")
    base       = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base, "models")
    cm_count   = 0

    for ex in EXERCISES:
        files_ok = all(
            os.path.isfile(os.path.join(models_dir, pat.format(ex)))
            for pat in MODEL_FILES
        )
        if files_ok:
            ok(f"{ex:<20}  model + encoder + features")
        else:
            if sys.platform == "win32":
                py_cmd = r"venv\Scripts\python"
            else:
                py_cmd = "venv/bin/python"
            add_issue(
                f"Model files missing for: {ex}",
                f"Run:  {py_cmd} train_model.py  (choose option 2)"
            )
        if os.path.isfile(os.path.join(models_dir, f"{ex}_confusion_matrix.png")):
            cm_count += 1

    if cm_count == len(EXERCISES):
        ok(f"Confusion matrix plots: {cm_count}/{len(EXERCISES)}")
    else:
        add_warn(f"Confusion matrix plots: {cm_count}/{len(EXERCISES)}")

# ════════════════════════════════════════════════════════════════════
# 7. MODULE IMPORT TEST
# ════════════════════════════════════════════════════════════════════
def check_modules():
    section("Module Import Test")
    modules_to_test = [
        ("config",                            "config"),
        ("utils.pose_detector",               "PoseDetector"),
        ("utils.angle_calculator",            "AngleCalculator"),
        ("utils.feedback_generator",          "FeedbackGenerator"),
        ("exercises.squat_analyzer",          "SquatAnalyzer"),
        ("exercises.pushup_analyzer",         "PushupAnalyzer"),
        ("exercises.bicep_curl_analyzer",     "BicepCurlAnalyzer"),
        ("exercises.lunge_analyzer",          "LungeAnalyzer"),
        ("exercises.shoulder_press_analyzer", "ShoulderPressAnalyzer"),
    ]
    for mod_name, class_name in modules_to_test:
        try:
            mod = importlib.import_module(mod_name)
            if class_name != mod_name:
                getattr(mod, class_name)
            ok(f"{mod_name}  ->  {class_name}")
        except ImportError as e:
            add_issue(f"Cannot import {mod_name}: {e}", "Check file exists with no syntax errors")
        except AttributeError as e:
            add_issue(f"Class {class_name} missing in {mod_name}: {e}", "")
        except Exception as e:
            add_issue(f"Error loading {mod_name}: {e}", "")

# ════════════════════════════════════════════════════════════════════
# 8. ANGLE CALCULATOR LOGIC
# ════════════════════════════════════════════════════════════════════
def check_angle_calc():
    section("Angle Calculator Logic Test")
    try:
        from utils.angle_calculator import AngleCalculator
        calc = AngleCalculator()

        a = calc.calculate_angle((0,0), (0,1), (1,1))
        assert 88 <= a <= 92, f"Expected ~90, got {a}"
        ok(f"Right-angle test   : {a} degrees  (expected 90)")

        a = calc.calculate_angle((0,0), (1,0), (2,0))
        assert 178 <= a <= 182, f"Expected ~180, got {a}"
        ok(f"Straight-line test : {a} degrees  (expected 180)")

        d = calc.calculate_distance((0,0), (3,4))
        assert abs(d - 5.0) < 0.01, f"Expected 5.0, got {d}"
        ok(f"Distance test      : {d}  (expected 5.0)")

        info("All angle calculations verified")
    except Exception as e:
        add_issue(f"Angle calculator test failed: {e}", "")

# ════════════════════════════════════════════════════════════════════
# 9. EXERCISE ANALYZER SMOKE TEST
# ════════════════════════════════════════════════════════════════════
def check_analyzers():
    section("Exercise Analyzer Tests")
    import numpy as np
    try:
        from exercises.squat_analyzer          import SquatAnalyzer
        from exercises.pushup_analyzer         import PushupAnalyzer
        from exercises.bicep_curl_analyzer     import BicepCurlAnalyzer
        from exercises.lunge_analyzer          import LungeAnalyzer
        from exercises.shoulder_press_analyzer import ShoulderPressAnalyzer

        mock = {i: (0.5 + np.random.uniform(-0.05, 0.05),
                    0.05 + i * 0.028, 0.0, 0.98) for i in range(33)}

        analyzers = {
            "Squat":          SquatAnalyzer(),
            "Pushup":         PushupAnalyzer(),
            "Bicep Curl":     BicepCurlAnalyzer(),
            "Lunge":          LungeAnalyzer(),
            "Shoulder Press": ShoulderPressAnalyzer(),
        }

        for name, analyzer in analyzers.items():
            r = analyzer.analyze(mock)
            assert "rep_count"  in r
            assert "stage"      in r
            assert "feedback"   in r
            assert "form_score" in r
            ok(f"{name:<20}  stage={r['stage']:<12}  form={r['form_score']}%")

        info("All 5 exercise analyzers functional")
    except Exception as e:
        add_issue(f"Analyzer test failed: {e}", "")

# ════════════════════════════════════════════════════════════════════
# 10. ML PREDICTION TEST
# ════════════════════════════════════════════════════════════════════
def check_ml_predict():
    section("ML Model Load & Predict Test")
    try:
        from train_model import PosturePredictor

        test_cases = {
            "squat": {
                "left_knee_angle": 85.0, "right_knee_angle": 87.0,
                "left_hip_angle":  80.0, "right_hip_angle":  82.0,
                "back_angle":     165.0,
            },
            "pushup": {
                "left_elbow_angle":  88.0, "right_elbow_angle": 90.0,
                "left_body_angle":  170.0, "right_body_angle": 169.0,
            },
            "bicep_curl": {
                "left_elbow_angle":    35.0, "right_elbow_angle":    37.0,
                "left_shoulder_angle": 10.0, "right_shoulder_angle": 11.0,
            },
            "lunge": {
                "left_knee_angle":  90.0, "right_knee_angle": 140.0,
                "left_hip_angle":  165.0,
            },
            "shoulder_press": {
                "left_elbow_angle":    170.0, "right_elbow_angle":    168.0,
                "left_shoulder_angle": 170.0, "right_shoulder_angle": 172.0,
            },
        }

        for ex, angles in test_cases.items():
            p = PosturePredictor(ex)
            if p.model is None:
                add_issue(f"Model not loaded for {ex}",
                          "Run train_model.py -> option 2")
                continue
            label, conf = p.predict(angles)
            ok(f"{ex:<15}  prediction={label:<12}  confidence={conf:.2f}")

        info("ML model prediction pipeline functional (all 5 exercises)")
    except Exception as e:
        add_issue(f"ML predict test failed: {e}", "")

# ════════════════════════════════════════════════════════════════════
# 11. FLASK ROUTE TEST
# ════════════════════════════════════════════════════════════════════
def check_flask_routes():
    section("Flask Application Routes Test")
    try:
        import importlib.util, json
        base = os.path.dirname(os.path.abspath(__file__))
        spec = importlib.util.spec_from_file_location(
            "web_app", os.path.join(base, "web_app.py"))
        web  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(web)

        flask_app = web.app
        with flask_app.test_client() as client:
            for method, url, body in [
                ("GET",  "/",                     None),
                ("GET",  "/exercise?type=squat",  None),
                ("GET",  "/history",              None),
                ("GET",  "/get_analysis",         None),
                ("POST", "/set_exercise",         {"exercise": "squat"}),
                ("POST", "/reset_counter",        {}),
            ]:
                if method == "GET":
                    r = client.get(url)
                else:
                    r = client.post(url,
                                    data=json.dumps(body),
                                    content_type="application/json")
                status = r.status_code
                sym = OK_SYM if status == 200 else FAIL_SYM
                color = GREEN if status == 200 else RED
                print(f"  {color}{sym}{RESET}  {method:<5} {url:<30}  HTTP {status}")
                if status != 200:
                    add_issue(f"{method} {url} returned HTTP {status}", "")

        info("All Flask routes responding correctly")
    except Exception as e:
        add_issue(f"Flask route test failed: {e}", "")

# ════════════════════════════════════════════════════════════════════
# 12. CAMERA CHECK
# ════════════════════════════════════════════════════════════════════
def check_camera():
    section("Webcam / Camera")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                ok(f"Camera (index 0) working  --  frame size: {w}x{h}")
            else:
                add_warn("Camera opened but could not read a frame")
        else:
            add_warn("Camera not detected at index 0 (connect a webcam before starting exercises)")
            info("Camera is only needed at runtime — setup can continue without it")
    except Exception as e:
        add_warn(f"Camera check skipped: {e}")

# ════════════════════════════════════════════════════════════════════
# 13. PORT CHECK
# ════════════════════════════════════════════════════════════════════
def check_port():
    section("Network Port (5000)")
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex(("127.0.0.1", 5000))
    s.close()
    if result == 0:
        add_warn("Port 5000 is already in use — STOP.bat will close it before starting")
    else:
        ok("Port 5000 is free and available")

# ════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════
def summary():
    print(f"\n{BLUE}{BOLD}{'=' * 64}{RESET}")
    print(f"{BOLD}  DIAGNOSTIC SUMMARY{RESET}")
    print(f"{BLUE}{'=' * 64}{RESET}")

    if not issues and not warnings:
        print(f"""
  {GREEN}{BOLD}[OK]  ALL CHECKS PASSED -- System is fully operational!{RESET}

  {WHITE}Everything is configured correctly:{RESET}
    Python version         OK
    Virtual environment    OK
    All source files       OK  ({len(REQUIRED_FILES)} files)
    All folders            OK
    All pip packages       OK
    All 5 ML models        trained and loadable
    All exercise analyzers functional
    All Flask routes       responding
    Webcam                 detected
""")
        return True

    if warnings:
        print(f"\n  {YELLOW}{BOLD}Warnings ({len(warnings)}):{RESET}")
        for w in warnings:
            print(f"    {YELLOW}[??]  {w}{RESET}")

    if issues:
        print(f"\n  {RED}{BOLD}Issues Found ({len(issues)}) -- Fix before running:{RESET}")
        for i, (msg, fix) in enumerate(issues, 1):
            print(f"\n  {RED}{i}. {msg}{RESET}")
            if fix:
                print(f"     {YELLOW}->  {fix}{RESET}")
        print(f"""
{RED}{BOLD}  [!!]  {len(issues)} issue(s) must be resolved.{RESET}
{YELLOW}        Fix the items above and re-run START.bat{RESET}
""")
        return False

    print(f"\n  {GREEN}{BOLD}[OK]  Passed with {len(warnings)} warning(s) -- App can start.{RESET}\n")
    return True

# ════════════════════════════════════════════════════════════════════
def main():
    banner()
    check_python()
    check_venv()
    check_folders()
    check_source_files()
    check_packages()
    check_models()
    check_modules()
    check_angle_calc()
    check_analyzers()
    check_ml_predict()
    check_flask_routes()
    check_camera()
    check_port()
    ok_to_run = summary()
    sys.exit(0 if ok_to_run else 1)

if __name__ == "__main__":
    main()
