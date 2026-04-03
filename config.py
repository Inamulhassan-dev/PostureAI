"""
config.py - Configuration settings for the Exercise Posture System
"""
import os

# ============ PATHS ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
COLLECTED_DATA_DIR = os.path.join(DATA_DIR, 'collected')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# ============ CAMERA SETTINGS ============
CAMERA_INDEX = 0        # 0 for default webcam
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

# ============ MEDIAPIPE SETTINGS ============
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
MODEL_COMPLEXITY = 1    # 0=Lite, 1=Full, 2=Heavy

# ============ EXERCISE SETTINGS ============
SUPPORTED_EXERCISES = [
    'squat',
    'pushup',
    'bicep_curl',
    'lunge',
    'shoulder_press'
]

# ============ ANGLE THRESHOLDS ============
EXERCISE_THRESHOLDS = {
    'squat': {
        'knee_angle_min': 70,
        'knee_angle_max': 100,
        'hip_angle_min': 60,
        'hip_angle_max': 100,
        'back_angle_min': 150,
        'standing_angle': 160,
    },
    'pushup': {
        'elbow_angle_down': 90,
        'elbow_angle_up': 160,
        'body_angle_min': 160,
        'elbow_tolerance': 20,
    },
    'bicep_curl': {
        'elbow_angle_up': 40,
        'elbow_angle_down': 160,
        'shoulder_movement_max': 15,
    },
    'lunge': {
        'front_knee_angle': 90,
        'back_knee_angle': 90,
        'torso_angle_min': 160,
        'tolerance': 20,
    },
    'shoulder_press': {
        'elbow_angle_up': 170,
        'elbow_angle_down': 90,
        'shoulder_alignment': 10,
    }
}

# ============ FEEDBACK COLORS (BGR format for OpenCV) ============
COLOR_CORRECT   = (0, 255, 0)       # Green
COLOR_INCORRECT = (0, 0, 255)       # Red
COLOR_WARNING   = (0, 165, 255)     # Orange
COLOR_INFO      = (255, 255, 0)     # Cyan
COLOR_WHITE     = (255, 255, 255)
COLOR_BLACK     = (0, 0, 0)

# ============ FONT SETTINGS ============
FONT_SCALE = 0.7
FONT_THICKNESS = 2

# ============ ML MODEL SETTINGS ============
TEST_SIZE = 0.2
RANDOM_STATE = 42
