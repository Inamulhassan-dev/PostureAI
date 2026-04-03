"""
main_app.py - Main standalone application
Real-time exercise posture analysis using webcam
"""
import cv2
import time
import numpy as np
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
    SUPPORTED_EXERCISES, COLOR_WHITE, COLOR_INFO,
    COLOR_CORRECT, COLOR_INCORRECT
)


class ExercisePostureApp:
    """Main application for real-time exercise posture analysis."""

    def __init__(self):
        self.pose_detector = PoseDetector()
        self.feedback_gen = FeedbackGenerator(use_voice=False)

        self.analyzers = {
            'squat': SquatAnalyzer(),
            'pushup': PushupAnalyzer(),
            'bicep_curl': BicepCurlAnalyzer(),
            'lunge': LungeAnalyzer(),
            'shoulder_press': ShoulderPressAnalyzer(),
        }

        self.current_exercise = 'squat'
        self.is_running = False
        self.fps = 0
        self.prev_time = time.time()

    def calculate_fps(self):
        """Calculate frames per second."""
        current_time = time.time()
        elapsed = current_time - self.prev_time
        if elapsed > 0:
            self.fps = 1.0 / elapsed
        self.prev_time = current_time

    def draw_hud(self, frame):
        """Draw HUD overlay with controls."""
        h, w = frame.shape[:2]

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 80), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

        controls = "1:Squat | 2:Pushup | 3:Bicep Curl | 4:Lunge | 5:Shoulder Press | R:Reset | Q:Quit"
        cv2.putText(frame, controls, (10, h - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_WHITE, 1)

        fps_text = f"FPS: {int(self.fps)}"
        cv2.putText(frame, fps_text, (w - 120, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_INFO, 2)

        return frame

    def run(self):
        """Main application loop."""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        if not cap.isOpened():
            print("Cannot open camera!")
            return

        print("\n" + "="*60)
        print(" INTELLIGENT EXERCISE POSTURE ANALYSIS SYSTEM")
        print("="*60)
        print("\nControls:")
        print("  1-5 : Switch exercise")
        print("  r   : Reset rep counter")
        print("  q/ESC: Quit")
        print("="*60)

        self.is_running = True

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read camera frame.")
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            self.calculate_fps()

            # Detect pose
            frame, results = self.pose_detector.detect_pose(frame)

            if self.pose_detector.is_pose_detected():
                landmarks = self.pose_detector.get_all_landmarks()

                # Analyze exercise
                analyzer = self.analyzers[self.current_exercise]
                analysis = analyzer.analyze(landmarks)

                # Draw landmarks
                lm_color = (0, 255, 0) if analysis['is_correct'] else (0, 0, 255)
                conn_color = (0, 200, 0) if analysis['is_correct'] else (0, 0, 200)

                frame = self.pose_detector.draw_landmarks(
                    frame,
                    landmark_color=lm_color,
                    connection_color=conn_color
                )

                # Draw feedback
                frame = self.feedback_gen.draw_feedback_on_frame(
                    frame,
                    analysis['feedback'],
                    rep_count=analysis['rep_count'],
                    exercise_name=self.current_exercise.replace('_', ' '),
                    stage=analysis['stage']
                )

                # Draw angles
                frame = self.feedback_gen.draw_angles_on_frame(
                    frame, analysis['angles'], landmarks, frame.shape
                )

                # Form score bar
                score = analysis.get('form_score', 100)
                bar_width = int((score / 100) * 200)
                if score > 70:
                    bar_color = COLOR_CORRECT
                elif score > 40:
                    bar_color = (0, 165, 255)
                else:
                    bar_color = COLOR_INCORRECT

                cv2.rectangle(frame, (w - 250, 90), (w - 50, 110), (50, 50, 50), -1)
                cv2.rectangle(frame, (w - 250, 90), (w - 250 + bar_width, 110), bar_color, -1)
                cv2.putText(frame, f"Form: {score}%", (w - 250, 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_WHITE, 1)

            else:
                cv2.putText(frame, "No person detected. Step into frame.",
                            (w // 6, h // 2), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 0, 255), 2)

            frame = self.draw_hud(frame)
            cv2.imshow("Exercise Posture Analysis", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:
                self.is_running = False
            elif key == ord('1'):
                self.current_exercise = 'squat'
                self.analyzers[self.current_exercise].reset()
                print("Switched to: Squat")
            elif key == ord('2'):
                self.current_exercise = 'pushup'
                self.analyzers[self.current_exercise].reset()
                print("Switched to: Push-up")
            elif key == ord('3'):
                self.current_exercise = 'bicep_curl'
                self.analyzers[self.current_exercise].reset()
                print("Switched to: Bicep Curl")
            elif key == ord('4'):
                self.current_exercise = 'lunge'
                self.analyzers[self.current_exercise].reset()
                print("Switched to: Lunge")
            elif key == ord('5'):
                self.current_exercise = 'shoulder_press'
                self.analyzers[self.current_exercise].reset()
                print("Switched to: Shoulder Press")
            elif key == ord('r'):
                self.analyzers[self.current_exercise].reset()
                print("Counter reset!")

        cap.release()
        cv2.destroyAllWindows()
        self.pose_detector.release()
        print("\nApplication closed.")


if __name__ == "__main__":
    app = ExercisePostureApp()
    app.run()
