"""
pushup_analyzer.py - Push-up exercise posture analyzer
"""
from utils.angle_calculator import AngleCalculator, get_exercise_angles
from config import EXERCISE_THRESHOLDS


class PushupAnalyzer:
    """Analyzes push-up posture, counts reps, and provides feedback."""

    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.thresholds = EXERCISE_THRESHOLDS['pushup']
        self.rep_count = 0
        self.stage = "up"
        self.prev_elbow_angle = 180

    def analyze(self, landmarks):
        result = {
            'angles': {},
            'feedback': [],
            'rep_count': self.rep_count,
            'stage': self.stage,
            'is_correct': True,
            'form_score': 100
        }

        angles = get_exercise_angles(landmarks, 'pushup')
        result['angles'] = angles

        if not angles:
            return result

        elbow_angle = self._get_avg(angles, 'left_elbow', 'right_elbow')
        body_angle = self._get_avg(angles, 'left_body', 'right_body')

        if elbow_angle is None:
            return result

        # Rep counting
        self._count_reps(elbow_angle)
        result['rep_count'] = self.rep_count
        result['stage'] = self.stage

        form_score = 100

        # Check body alignment
        if body_angle is not None:
            if body_angle < 150:
                result['feedback'].append(("Hips too high! Straighten body.", (0, 0, 255)))
                form_score -= 25
                result['is_correct'] = False
            elif body_angle < self.thresholds['body_angle_min']:
                result['feedback'].append(("Hips sagging! Engage core.", (0, 0, 255)))
                form_score -= 25
                result['is_correct'] = False
            else:
                result['feedback'].append(("Body alignment good!", (0, 255, 0)))

        # Check depth
        if self.stage == 'down':
            tolerance = self.thresholds.get('elbow_tolerance', 20)
            if elbow_angle > self.thresholds['elbow_angle_down'] + tolerance:
                result['feedback'].append(("Go lower!", (0, 165, 255)))
                form_score -= 15
            else:
                result['feedback'].append(("Good depth!", (0, 255, 0)))

        result['form_score'] = max(0, form_score)
        return result

    def _count_reps(self, elbow_angle):
        up_threshold = self.thresholds['elbow_angle_up']
        down_threshold = self.thresholds['elbow_angle_down']

        if elbow_angle > up_threshold:
            if self.stage == 'down':
                self.rep_count += 1
            self.stage = 'up'
        elif elbow_angle < down_threshold:
            self.stage = 'down'

    def _get_avg(self, angles, k1, k2):
        v1 = angles.get(k1)
        v2 = angles.get(k2)
        if v1 is not None and v2 is not None:
            return (v1 + v2) / 2
        elif v1 is not None:
            return v1
        return v2

    def reset(self):
        self.rep_count = 0
        self.stage = "up"
        self.prev_elbow_angle = 180
