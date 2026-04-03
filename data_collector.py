"""
data_collector.py - Collect pose data for ML training
Records body landmarks while performing exercises with labels
"""
import cv2
import csv
import os
import time
import numpy as np
from datetime import datetime
from utils.pose_detector import PoseDetector
from utils.angle_calculator import AngleCalculator, get_exercise_angles
from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    COLLECTED_DATA_DIR, SUPPORTED_EXERCISES,
    COLOR_CORRECT, COLOR_INCORRECT, COLOR_WHITE, COLOR_INFO
)


class DataCollector:
    """Collect pose landmark data with labels for training ML models."""

    def __init__(self):
        self.pose_detector = PoseDetector()
        self.angle_calculator = AngleCalculator()
        self.data = []
        self.is_recording = False
        self.current_label = "correct"
        self.current_exercise = "squat"

    def create_csv_header(self, exercise_type):
        """Create CSV header with landmark coordinates and angles."""
        headers = []

        for i in range(33):
            headers.extend([
                f'landmark_{i}_x', f'landmark_{i}_y',
                f'landmark_{i}_z', f'landmark_{i}_vis'
            ])

        if exercise_type == 'squat':
            headers.extend(['left_knee_angle', 'right_knee_angle',
                            'left_hip_angle', 'right_hip_angle', 'back_angle'])
        elif exercise_type == 'pushup':
            headers.extend(['left_elbow_angle', 'right_elbow_angle',
                            'left_body_angle', 'right_body_angle'])
        elif exercise_type == 'bicep_curl':
            headers.extend(['left_elbow_angle', 'right_elbow_angle',
                            'left_shoulder_angle', 'right_shoulder_angle'])
        elif exercise_type == 'lunge':
            headers.extend(['left_knee_angle', 'right_knee_angle', 'left_hip_angle'])
        elif exercise_type == 'shoulder_press':
            headers.extend(['left_elbow_angle', 'right_elbow_angle',
                            'left_shoulder_angle', 'right_shoulder_angle'])

        headers.append('label')
        headers.append('exercise_stage')
        return headers

    def collect_frame_data(self, exercise_type, label, stage=""):
        """Collect data from current frame."""
        if not self.pose_detector.is_pose_detected():
            return None

        row = []
        landmark_array = self.pose_detector.get_landmarks_as_array()
        if landmark_array is None:
            return None

        row.extend(landmark_array.tolist())

        landmarks = self.pose_detector.get_all_landmarks()
        angles = get_exercise_angles(landmarks, exercise_type)

        if exercise_type == 'squat':
            row.extend([angles.get('left_knee', 0), angles.get('right_knee', 0),
                        angles.get('left_hip', 0), angles.get('right_hip', 0),
                        angles.get('left_back', 0)])
        elif exercise_type == 'pushup':
            row.extend([angles.get('left_elbow', 0), angles.get('right_elbow', 0),
                        angles.get('left_body', 0), angles.get('right_body', 0)])
        elif exercise_type == 'bicep_curl':
            row.extend([angles.get('left_elbow', 0), angles.get('right_elbow', 0),
                        angles.get('left_shoulder', 0), angles.get('right_shoulder', 0)])
        elif exercise_type == 'lunge':
            row.extend([angles.get('left_knee', 0), angles.get('right_knee', 0),
                        angles.get('left_hip', 0)])
        elif exercise_type == 'shoulder_press':
            row.extend([angles.get('left_elbow', 0), angles.get('right_elbow', 0),
                        angles.get('left_shoulder', 0), angles.get('right_shoulder', 0)])

        row.append(label)
        row.append(stage)
        return row

    def save_data(self, exercise_type, data_rows):
        """Save collected data to CSV file."""
        os.makedirs(COLLECTED_DATA_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{exercise_type}_data_{timestamp}.csv"
        filepath = os.path.join(COLLECTED_DATA_DIR, filename)

        headers = self.create_csv_header(exercise_type)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data_rows)

        print(f"Saved {len(data_rows)} samples to {filepath}")
        return filepath

    def run_collection(self):
        """Run the interactive data collection interface."""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        if not cap.isOpened():
            print("Cannot open camera!")
            return

        print("\n" + "="*60)
        print(" EXERCISE POSTURE DATA COLLECTOR")
        print("="*60)
        print("\nControls:")
        print(" 1-5 : Select exercise")
        print(" c   : Label = CORRECT")
        print(" i   : Label = INCORRECT")
        print(" u   : Stage = UP")
        print(" d   : Stage = DOWN")
        print(" SPACE: Toggle recording ON/OFF")
        print(" s   : Save data")
        print(" r   : Reset/clear data")
        print(" q   : Quit")
        print("="*60)

        collected_data = []
        stage = "standing"

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame, results = self.pose_detector.detect_pose(frame)

            if self.pose_detector.is_pose_detected():
                frame = self.pose_detector.draw_landmarks(frame)
                landmarks = self.pose_detector.get_all_landmarks()
                angles = get_exercise_angles(landmarks, self.current_exercise)

                y_offset = 150
                for name, value in angles.items():
                    cv2.putText(frame, f"{name}: {value:.1f}",
                                (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, COLOR_WHITE, 2)
                    y_offset += 25

                if self.is_recording:
                    row = self.collect_frame_data(self.current_exercise, self.current_label, stage)
                    if row:
                        collected_data.append(row)

            h, w = frame.shape[:2]
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 120), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

            cv2.putText(frame, f"Exercise: {self.current_exercise.upper()}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_WHITE, 2)

            label_color = COLOR_CORRECT if self.current_label == "correct" else COLOR_INCORRECT
            cv2.putText(frame, f"Label: {self.current_label.upper()}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, label_color, 2)

            cv2.putText(frame, f"Stage: {stage.upper()}",
                        (350, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_INFO, 2)

            rec_color = (0, 0, 255) if self.is_recording else (128, 128, 128)
            rec_text = "RECORDING" if self.is_recording else "NOT RECORDING"
            cv2.putText(frame, rec_text, (10, 95),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, rec_color, 2)

            cv2.putText(frame, f"Samples: {len(collected_data)}",
                        (350, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 2)

            cv2.imshow("Data Collector", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1'):
                self.current_exercise = 'squat'
            elif key == ord('2'):
                self.current_exercise = 'pushup'
            elif key == ord('3'):
                self.current_exercise = 'bicep_curl'
            elif key == ord('4'):
                self.current_exercise = 'lunge'
            elif key == ord('5'):
                self.current_exercise = 'shoulder_press'
            elif key == ord('c'):
                self.current_label = 'correct'
            elif key == ord('i'):
                self.current_label = 'incorrect'
            elif key == ord('u'):
                stage = 'up'
            elif key == ord('d'):
                stage = 'down'
            elif key == ord(' '):
                self.is_recording = not self.is_recording
                print(f"Recording {'STARTED' if self.is_recording else 'STOPPED'}")
            elif key == ord('s'):
                if collected_data:
                    self.save_data(self.current_exercise, collected_data)
                else:
                    print("No data to save!")
            elif key == ord('r'):
                collected_data = []
                print("Data cleared!")

        cap.release()
        cv2.destroyAllWindows()
        self.pose_detector.release()

        if collected_data:
            save = input("Save collected data before exit? (y/n): ")
            if save.lower() == 'y':
                self.save_data(self.current_exercise, collected_data)


if __name__ == "__main__":
    collector = DataCollector()
    collector.run_collection()
