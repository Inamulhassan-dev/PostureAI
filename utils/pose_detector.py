"""
pose_detector.py - MediaPipe Pose Detection Wrapper
Handles all pose estimation functionality
"""
import cv2
import mediapipe as mp
import numpy as np
from config import (
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MODEL_COMPLEXITY
)


class PoseDetector:
    """
    Wrapper class for MediaPipe Pose detection.
    Provides easy-to-use methods for detecting human pose landmarks.
    """

    def __init__(self,
                 static_image_mode=False,
                 model_complexity=MODEL_COMPLEXITY,
                 smooth_landmarks=True,
                 enable_segmentation=False,
                 min_detection_confidence=MIN_DETECTION_CONFIDENCE,
                 min_tracking_confidence=MIN_TRACKING_CONFIDENCE):
        """Initialize the PoseDetector with MediaPipe Pose."""
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        self.results = None
        self.landmarks = None

        # Landmark name mapping for easier access
        self.landmark_names = {
            0: 'NOSE',
            1: 'LEFT_EYE_INNER', 2: 'LEFT_EYE', 3: 'LEFT_EYE_OUTER',
            4: 'RIGHT_EYE_INNER', 5: 'RIGHT_EYE', 6: 'RIGHT_EYE_OUTER',
            7: 'LEFT_EAR', 8: 'RIGHT_EAR',
            9: 'MOUTH_LEFT', 10: 'MOUTH_RIGHT',
            11: 'LEFT_SHOULDER', 12: 'RIGHT_SHOULDER',
            13: 'LEFT_ELBOW', 14: 'RIGHT_ELBOW',
            15: 'LEFT_WRIST', 16: 'RIGHT_WRIST',
            17: 'LEFT_PINKY', 18: 'RIGHT_PINKY',
            19: 'LEFT_INDEX', 20: 'RIGHT_INDEX',
            21: 'LEFT_THUMB', 22: 'RIGHT_THUMB',
            23: 'LEFT_HIP', 24: 'RIGHT_HIP',
            25: 'LEFT_KNEE', 26: 'RIGHT_KNEE',
            27: 'LEFT_ANKLE', 28: 'RIGHT_ANKLE',
            29: 'LEFT_HEEL', 30: 'RIGHT_HEEL',
            31: 'LEFT_FOOT_INDEX', 32: 'RIGHT_FOOT_INDEX'
        }

    def detect_pose(self, frame):
        """
        Detect pose landmarks in a frame.

        Args:
            frame: BGR image from OpenCV

        Returns:
            frame: Original frame (unchanged)
            results: MediaPipe pose results
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        # Process the frame
        self.results = self.pose.process(rgb_frame)

        # Extract landmarks if detected
        if self.results.pose_landmarks:
            self.landmarks = self.results.pose_landmarks.landmark
        else:
            self.landmarks = None

        return frame, self.results

    def draw_landmarks(self, frame, draw_connections=True,
                       landmark_color=(0, 255, 0),
                       connection_color=(255, 255, 255)):
        """
        Draw detected landmarks on the frame.

        Args:
            frame: Image to draw on
            draw_connections: Whether to draw skeleton connections
            landmark_color: Color for landmark points
            connection_color: Color for connection lines
        """
        if self.results and self.results.pose_landmarks:
            landmark_spec = self.mp_drawing.DrawingSpec(
                color=landmark_color,
                thickness=2,
                circle_radius=3
            )
            connection_spec = self.mp_drawing.DrawingSpec(
                color=connection_color,
                thickness=2,
                circle_radius=1
            )

            self.mp_drawing.draw_landmarks(
                frame,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS if draw_connections else None,
                landmark_spec,
                connection_spec
            )

        return frame

    def get_landmark(self, landmark_id, frame_shape=None):
        """
        Get a specific landmark's coordinates.

        Args:
            landmark_id: Index of the landmark (0-32)
            frame_shape: (height, width) to convert to pixel coordinates

        Returns:
            tuple: (x, y, z, visibility) or None if not detected
        """
        if self.landmarks is None:
            return None

        if landmark_id < 0 or landmark_id >= len(self.landmarks):
            return None

        lm = self.landmarks[landmark_id]

        if frame_shape:
            h, w = frame_shape[:2]
            return (int(lm.x * w), int(lm.y * h), lm.z, lm.visibility)

        return (lm.x, lm.y, lm.z, lm.visibility)

    def get_all_landmarks(self, frame_shape=None):
        """
        Get all 33 landmarks as a dictionary.

        Args:
            frame_shape: (height, width) for pixel coordinates

        Returns:
            dict: {landmark_id: (x, y, z, visibility)}
        """
        if self.landmarks is None:
            return None

        all_landmarks = {}
        for idx in range(33):
            lm = self.get_landmark(idx, frame_shape)
            if lm:
                all_landmarks[idx] = lm

        return all_landmarks

    def get_landmarks_as_array(self):
        """
        Get all landmarks as a flat numpy array.
        Useful for ML model input.

        Returns:
            numpy array of shape (132,) - 33 landmarks x 4 values each
        """
        if self.landmarks is None:
            return None

        landmark_array = []
        for lm in self.landmarks:
            landmark_array.extend([lm.x, lm.y, lm.z, lm.visibility])

        return np.array(landmark_array)

    def is_pose_detected(self):
        """Check if a pose was detected in the last frame."""
        return self.landmarks is not None

    def get_visibility(self, landmark_id):
        """Get the visibility score of a specific landmark."""
        if self.landmarks is None:
            return 0
        return self.landmarks[landmark_id].visibility

    def release(self):
        """Release MediaPipe resources."""
        self.pose.close()
