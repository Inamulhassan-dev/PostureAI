"""
squat_analyzer.py - Squat exercise posture analyzer
Handles squat-specific posture analysis, rep counting, and feedback
"""
from utils.angle_calculator import AngleCalculator, get_exercise_angles
from config import EXERCISE_THRESHOLDS


class SquatAnalyzer:
    """
    Analyzes squat exercise posture, counts reps, and provides feedback.
    """

    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.thresholds = EXERCISE_THRESHOLDS['squat']
        self.rep_count = 0
        self.stage = "standing"
        self.prev_knee_angle = 180
        self.form_scores = []
        self.current_rep_errors = []

    def analyze(self, landmarks):
        """
        Analyze squat posture from landmarks.

        Returns:
            dict: Analysis results with angles, feedback, rep count, stage
        """
        result = {
            'angles': {},
            'feedback': [],
            'rep_count': self.rep_count,
            'stage': self.stage,
            'is_correct': True,
            'form_score': 100
        }

        angles = get_exercise_angles(landmarks, 'squat')
        result['angles'] = angles

        if not angles:
            result['feedback'].append(("Cannot detect pose properly", (0, 165, 255)))
            return result

        knee_angle = self._get_avg_angle(angles, 'left_knee', 'right_knee')
        hip_angle = self._get_avg_angle(angles, 'left_hip', 'right_hip')
        back_angle = angles.get('left_back', 180)

        if knee_angle is None:
            return result

        # Rep counting
        self._count_reps(knee_angle)
        result['rep_count'] = self.rep_count
        result['stage'] = self.stage

        # Posture analysis
        errors = []
        form_score = 100

        if self.stage in ['bottom', 'going_up']:
            if knee_angle > self.thresholds['knee_angle_max']:
                errors.append("Go deeper! Thighs parallel to ground.")
                form_score -= 20
            elif knee_angle < self.thresholds['knee_angle_min']:
                errors.append("Too deep! Stop when thighs are parallel.")
                form_score -= 15
            else:
                result['feedback'].append(("Good depth!", (0, 255, 0)))

        if back_angle < self.thresholds['back_angle_min']:
            errors.append("Keep back straight! Chest up!")
            form_score -= 25

        if 'left_knee' in angles and 'right_knee' in angles:
            knee_diff = abs(angles['left_knee'] - angles['right_knee'])
            if knee_diff > 15:
                errors.append("Knees uneven! Keep them symmetrical.")
                form_score -= 10

        if hip_angle is not None and self.stage == 'bottom':
            if hip_angle > self.thresholds['hip_angle_max']:
                errors.append("Bend at hips more!")
                form_score -= 15

        if self.stage == 'standing':
            result['feedback'].append(("Standing. Begin your squat.", (255, 255, 0)))

        for error in errors:
            result['feedback'].append((error, (0, 0, 255)))
            result['is_correct'] = False

        if not errors and self.stage != 'standing':
            result['feedback'].append(("Perfect form! Keep going!", (0, 255, 0)))

        result['form_score'] = max(0, form_score)
        return result

    def _count_reps(self, knee_angle):
        """Count squat repetitions based on knee angle transitions."""
        standing_threshold = self.thresholds['standing_angle']
        bottom_threshold = self.thresholds['knee_angle_max']

        if knee_angle > standing_threshold:
            if self.stage == 'going_up':
                self.rep_count += 1
                print(f"Rep #{self.rep_count} completed!")
            self.stage = 'standing'
        elif knee_angle < bottom_threshold:
            self.stage = 'bottom'
        elif knee_angle < self.prev_knee_angle:
            if self.stage in ['standing', 'going_up']:
                self.stage = 'going_down'
        elif knee_angle > self.prev_knee_angle:
            if self.stage in ['bottom', 'going_down']:
                self.stage = 'going_up'

        self.prev_knee_angle = knee_angle

    def _get_avg_angle(self, angles, left_key, right_key):
        """Get average of left and right angles."""
        left = angles.get(left_key)
        right = angles.get(right_key)

        if left is not None and right is not None:
            return (left + right) / 2
        elif left is not None:
            return left
        elif right is not None:
            return right
        return None

    def reset(self):
        """Reset the analyzer state."""
        self.rep_count = 0
        self.stage = "standing"
        self.prev_knee_angle = 180
        self.form_scores = []
        self.current_rep_errors = []
