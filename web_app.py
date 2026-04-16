"""
web_app.py - Flask web application for exercise posture analysis
Provides a browser-based interface with webcam streaming
"""
import cv2
import time
import json
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
import atexit
from utils.pose_detector import PoseDetector
from utils.feedback_generator import FeedbackGenerator
from utils.angle_calculator import get_exercise_angles
from exercises.squat_analyzer import SquatAnalyzer
from exercises.pushup_analyzer import PushupAnalyzer
from exercises.bicep_curl_analyzer import BicepCurlAnalyzer
from exercises.lunge_analyzer import LungeAnalyzer
from exercises.shoulder_press_analyzer import ShoulderPressAnalyzer
from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    SUPPORTED_EXERCISES, TEMPLATES_DIR, STATIC_DIR,
    COLOR_WHITE, COLOR_CORRECT, COLOR_INCORRECT, COLOR_INFO
)

# Initialize Flask App
app = Flask(__name__,
            template_folder=TEMPLATES_DIR,
            static_folder=STATIC_DIR)

# Global Variables
pose_detector = PoseDetector()
feedback_gen = FeedbackGenerator()
analyzers = {
    'squat': SquatAnalyzer(),
    'pushup': PushupAnalyzer(),
    'bicep_curl': BicepCurlAnalyzer(),
    'lunge': LungeAnalyzer(),
    'shoulder_press': ShoulderPressAnalyzer(),
}
current_exercise = 'squat'
latest_analysis = {}
camera = None


def cleanup_camera():
    """Release camera on application shutdown."""
    if camera is not None and camera.isOpened():
        camera.release()
        print("Camera released.")

atexit.register(cleanup_camera)


def get_camera():
    """Get or create camera instance."""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(CAMERA_INDEX)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    return camera


def generate_frames():
    """Generator function for video streaming."""
    global latest_analysis

    cap = get_camera()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        frame, results = pose_detector.detect_pose(frame)

        if pose_detector.is_pose_detected():
            landmarks = pose_detector.get_all_landmarks()
            analyzer = analyzers[current_exercise]
            analysis = analyzer.analyze(landmarks)
            latest_analysis = analysis

            lm_color = (0, 255, 0) if analysis['is_correct'] else (0, 0, 255)
            conn_color = (0, 200, 0) if analysis['is_correct'] else (0, 0, 200)

            frame = pose_detector.draw_landmarks(
                frame, landmark_color=lm_color, connection_color=conn_color)

            frame = feedback_gen.draw_feedback_on_frame(
                frame,
                analysis['feedback'],
                rep_count=analysis['rep_count'],
                exercise_name=current_exercise.replace('_', ' '),
                stage=analysis['stage']
            )

            frame = feedback_gen.draw_angles_on_frame(
                frame, analysis['angles'], landmarks, frame.shape)

            score = analysis.get('form_score', 100)
            bar_width = int((score / 100) * 200)
            bar_color = (0, 255, 0) if score > 70 else (0, 165, 255) if score > 40 else (0, 0, 255)
            cv2.rectangle(frame, (w - 250, 90), (w - 50, 110), (50, 50, 50), -1)
            cv2.rectangle(frame, (w - 250, 90), (w - 250 + bar_width, 110), bar_color, -1)
            cv2.putText(frame, f"Form: {score}%", (w - 250, 85),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_WHITE, 1)
        else:
            cv2.putText(frame, "Step into the camera frame",
                        (w // 4, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            latest_analysis = {}

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# ============ ROUTES ============

@app.route('/')
def index():
    """Home page with exercise selection."""
    return render_template('index.html', exercises=SUPPORTED_EXERCISES)


@app.route('/exercise')
def exercise_page():
    """Exercise analysis page."""
    exercise = request.args.get('type', 'squat')
    return render_template('exercise.html',
                           exercise=exercise,
                           exercises=SUPPORTED_EXERCISES)


@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    """API to change current exercise."""
    global current_exercise
    data = request.get_json()
    exercise = data.get('exercise', 'squat')

    if exercise in SUPPORTED_EXERCISES:
        current_exercise = exercise
        analyzers[exercise].reset()
        return jsonify({'status': 'success', 'exercise': exercise})

    return jsonify({'status': 'error', 'message': 'Invalid exercise'}), 400


@app.route('/get_analysis')
def get_analysis():
    """API to get latest analysis data."""
    if latest_analysis:
        feedback_data = []
        for msg, color in latest_analysis.get('feedback', []):
            if color == (0, 255, 0):
                ftype = 'correct'
            elif color == (0, 0, 255):
                ftype = 'incorrect'
            else:
                ftype = 'warning'
            feedback_data.append({'message': msg, 'type': ftype})

        return jsonify({
            'rep_count': latest_analysis.get('rep_count', 0),
            'stage': latest_analysis.get('stage', ''),
            'is_correct': latest_analysis.get('is_correct', True),
            'form_score': latest_analysis.get('form_score', 0),
            'feedback': feedback_data,
            'angles': {k: round(v, 1) for k, v in latest_analysis.get('angles', {}).items()}
        })

    return jsonify({'rep_count': 0, 'stage': '', 'feedback': [], 'form_score': 0, 'is_correct': True, 'angles': {}})


@app.route('/reset_counter', methods=['POST'])
def reset_counter():
    """Reset rep counter for current exercise."""
    analyzers[current_exercise].reset()
    return jsonify({'status': 'success'})


@app.route('/history')
def history():
    """Workout history page."""
    return render_template('history.html')


if __name__ == '__main__':
    print("\n" + "="*60)
    print(" EXERCISE POSTURE ANALYSIS - WEB APPLICATION")
    print("="*60)
    print(f"\nOpen browser at: http://localhost:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
