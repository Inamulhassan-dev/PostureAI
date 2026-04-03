"""
feedback_generator.py - Generate posture correction feedback
Provides text and visual feedback based on posture analysis
"""
import cv2
import numpy as np
from config import (
    COLOR_CORRECT, COLOR_INCORRECT, COLOR_WARNING, COLOR_INFO,
    COLOR_WHITE, COLOR_BLACK, FONT_SCALE, FONT_THICKNESS,
    EXERCISE_THRESHOLDS
)

# Optional: Text-to-speech for voice feedback
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class FeedbackGenerator:
    """
    Generate visual and text feedback for exercise posture correction.
    """

    def __init__(self, use_voice=False):
        self.use_voice = use_voice and TTS_AVAILABLE

        if self.use_voice:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.last_voice_feedback = ""

        self.correction_messages = {
            'squat': {
                'knee_too_forward': "Warning: Knees going past toes! Push hips back.",
                'not_deep_enough': "Go deeper! Thighs should be parallel to ground.",
                'too_deep': "Don't go too deep! Stop at parallel.",
                'back_not_straight': "Keep your back straight! Chest up.",
                'knees_caving': "Push knees outward! Don't let them cave in.",
                'correct': "Perfect squat form! Keep going!",
                'standing': "Standing position. Start your squat."
            },
            'pushup': {
                'elbows_flaring': "Keep elbows closer to body!",
                'hips_sagging': "Lift your hips! Keep body in a straight line.",
                'hips_too_high': "Lower your hips! Body should be straight.",
                'not_low_enough': "Go lower! Chest should nearly touch ground.",
                'correct': "Great push-up form!",
                'up_position': "Good top position. Lower down."
            },
            'bicep_curl': {
                'swinging': "Don't swing! Keep upper arm still.",
                'not_full_curl': "Curl all the way up!",
                'not_full_extend': "Fully extend your arm at bottom.",
                'elbow_moving': "Pin your elbow to your side!",
                'correct': "Perfect curl form!",
            },
            'lunge': {
                'knee_past_toe': "Front knee past toes! Step further.",
                'back_not_straight': "Keep torso upright!",
                'not_deep_enough': "Lunge deeper! Back knee near ground.",
                'correct': "Great lunge form!",
            },
            'shoulder_press': {
                'not_full_extend': "Fully extend arms overhead!",
                'elbows_too_wide': "Keep elbows in front slightly.",
                'back_arching': "Don't arch your back!",
                'correct': "Perfect shoulder press!",
            }
        }

    def get_feedback(self, exercise_type, angles, stage=None):
        """
        Analyze angles and generate appropriate feedback.

        Returns:
            list: List of (message, color) tuples
        """
        feedback_list = []
        thresholds = EXERCISE_THRESHOLDS.get(exercise_type, {})
        messages = self.correction_messages.get(exercise_type, {})

        if exercise_type == 'squat':
            feedback_list = self._analyze_squat(angles, thresholds, messages)
        elif exercise_type == 'pushup':
            feedback_list = self._analyze_pushup(angles, thresholds, messages)
        elif exercise_type == 'bicep_curl':
            feedback_list = self._analyze_bicep_curl(angles, thresholds, messages)
        elif exercise_type == 'lunge':
            feedback_list = self._analyze_lunge(angles, thresholds, messages)
        elif exercise_type == 'shoulder_press':
            feedback_list = self._analyze_shoulder_press(angles, thresholds, messages)

        return feedback_list

    def _analyze_squat(self, angles, thresholds, messages):
        feedback = []

        knee_angle = None
        if 'left_knee' in angles and 'right_knee' in angles:
            knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
        elif 'left_knee' in angles:
            knee_angle = angles['left_knee']
        elif 'right_knee' in angles:
            knee_angle = angles['right_knee']

        hip_angle = None
        if 'left_hip' in angles and 'right_hip' in angles:
            hip_angle = (angles['left_hip'] + angles['right_hip']) / 2
        elif 'left_hip' in angles:
            hip_angle = angles['left_hip']

        if knee_angle is not None:
            if knee_angle > thresholds.get('standing_angle', 160):
                feedback.append((messages.get('standing', 'Standing'), COLOR_INFO))
            elif knee_angle < thresholds.get('knee_angle_min', 70):
                feedback.append((messages.get('too_deep', 'Too deep'), COLOR_WARNING))
            elif knee_angle > thresholds.get('knee_angle_max', 100):
                feedback.append((messages.get('not_deep_enough', 'Go deeper'), COLOR_WARNING))
            else:
                feedback.append((messages.get('correct', 'Good form'), COLOR_CORRECT))

        if 'left_back' in angles:
            back_angle = angles['left_back']
            if back_angle < thresholds.get('back_angle_min', 150):
                feedback.append((messages.get('back_not_straight', 'Straighten back'), COLOR_INCORRECT))

        return feedback

    def _analyze_pushup(self, angles, thresholds, messages):
        feedback = []

        elbow_angle = None
        if 'left_elbow' in angles and 'right_elbow' in angles:
            elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
        elif 'left_elbow' in angles:
            elbow_angle = angles['left_elbow']

        body_angle = None
        if 'left_body' in angles and 'right_body' in angles:
            body_angle = (angles['left_body'] + angles['right_body']) / 2
        elif 'left_body' in angles:
            body_angle = angles['left_body']

        if body_angle is not None:
            if body_angle < 150:
                feedback.append((messages.get('hips_too_high', 'Lower hips'), COLOR_WARNING))
            elif body_angle < thresholds.get('body_angle_min', 160):
                feedback.append((messages.get('hips_sagging', 'Lift hips'), COLOR_INCORRECT))

        if elbow_angle is not None:
            if elbow_angle > thresholds.get('elbow_angle_up', 160):
                feedback.append((messages.get('up_position', 'Top position'), COLOR_INFO))
            elif elbow_angle < thresholds.get('elbow_angle_down', 90) - 10:
                feedback.append((messages.get('correct', 'Good depth'), COLOR_CORRECT))
            else:
                feedback.append((messages.get('not_low_enough', 'Go lower'), COLOR_WARNING))

        return feedback

    def _analyze_bicep_curl(self, angles, thresholds, messages):
        feedback = []

        for side in ['left_elbow', 'right_elbow']:
            if side in angles:
                angle = angles[side]
                label = 'Left' if 'left' in side else 'Right'
                if angle < thresholds.get('elbow_angle_up', 40):
                    feedback.append((f"{label}: Fully curled!", COLOR_CORRECT))
                elif angle > thresholds.get('elbow_angle_down', 160):
                    feedback.append((f"{label}: Fully extended", COLOR_INFO))

        for side in ['left_shoulder', 'right_shoulder']:
            if side in angles:
                if angles[side] > 40:
                    feedback.append((messages.get('swinging', 'No swinging'), COLOR_INCORRECT))

        if not feedback:
            feedback.append((messages.get('correct', 'Good form'), COLOR_CORRECT))

        return feedback

    def _analyze_lunge(self, angles, thresholds, messages):
        feedback = []

        knee_angles = []
        if 'left_knee' in angles:
            knee_angles.append(angles['left_knee'])
        if 'right_knee' in angles:
            knee_angles.append(angles['right_knee'])

        if knee_angles:
            front_knee = min(knee_angles)
            if front_knee < 70:
                feedback.append((messages.get('knee_past_toe', 'Knee too far'), COLOR_INCORRECT))
            elif front_knee > 120:
                feedback.append((messages.get('not_deep_enough', 'Go deeper'), COLOR_WARNING))
            else:
                feedback.append((messages.get('correct', 'Good form'), COLOR_CORRECT))

        return feedback

    def _analyze_shoulder_press(self, angles, thresholds, messages):
        feedback = []

        elbow_angle = None
        if 'left_elbow' in angles and 'right_elbow' in angles:
            elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2

        if elbow_angle is not None:
            if elbow_angle > thresholds.get('elbow_angle_up', 170):
                feedback.append(("Arms fully extended!", COLOR_CORRECT))
            elif elbow_angle < thresholds.get('elbow_angle_down', 90):
                feedback.append(("Bottom position. Press up!", COLOR_INFO))
            else:
                feedback.append((messages.get('not_full_extend', 'Extend more'), COLOR_WARNING))

        return feedback

    def draw_feedback_on_frame(self, frame, feedback_list, rep_count=0,
                               exercise_name="", stage=""):
        """Draw feedback messages and info panel on the video frame."""
        h, w = frame.shape[:2]

        # Top info bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 100), COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        cv2.putText(frame, f"Exercise: {exercise_name.upper()}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_WHITE, 2)
        cv2.putText(frame, f"Reps: {rep_count}",
                    (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOR_INFO, 2)

        if stage:
            cv2.putText(frame, f"Stage: {stage.upper()}",
                        (250, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        COLOR_CORRECT if stage == 'up' else COLOR_WARNING, 2)

        # Feedback panel
        panel_x = w - 450
        panel_y = 120
        panel_width = 440
        panel_height = 40 * len(feedback_list) + 20

        if feedback_list:
            overlay2 = frame.copy()
            cv2.rectangle(overlay2, (panel_x - 10, panel_y - 10),
                          (panel_x + panel_width, panel_y + panel_height),
                          COLOR_BLACK, -1)
            cv2.addWeighted(overlay2, 0.7, frame, 0.3, 0, frame)

            for i, (message, color) in enumerate(feedback_list):
                y_pos = panel_y + 25 + (i * 35)
                cv2.putText(frame, message, (panel_x, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return frame

    def draw_angles_on_frame(self, frame, angles, landmarks, frame_shape):
        """Draw angle values near the corresponding joints on the frame."""
        if landmarks is None:
            return frame

        h, w = frame_shape[:2]

        angle_positions = {
            'left_knee': 25,
            'right_knee': 26,
            'left_hip': 23,
            'right_hip': 24,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_back': 11,
            'left_body': 23,
            'right_body': 24,
        }

        for angle_name, angle_value in angles.items():
            if angle_name in angle_positions:
                lm_id = angle_positions[angle_name]
                if lm_id in landmarks:
                    x = int(landmarks[lm_id][0] * w) if landmarks[lm_id][0] <= 1 else int(landmarks[lm_id][0])
                    y = int(landmarks[lm_id][1] * h) if landmarks[lm_id][1] <= 1 else int(landmarks[lm_id][1])

                    cv2.putText(frame, f"{int(angle_value)}",
                                (x - 30, y - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                COLOR_WHITE, 2)

        return frame

    def speak_feedback(self, message):
        """Provide voice feedback (if enabled)."""
        if self.use_voice and message != self.last_voice_feedback:
            self.last_voice_feedback = message
            try:
                self.engine.say(message)
                self.engine.runAndWait()
            except Exception:
                pass
