"""
bicep_curl_analyzer.py - Bicep curl exercise posture analyzer
"""
from utils.angle_calculator import AngleCalculator, get_exercise_angles
from config import EXERCISE_THRESHOLDS


class BicepCurlAnalyzer:
    """Analyzes bicep curl posture, counts reps, and provides feedback."""

    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.thresholds = EXERCISE_THRESHOLDS['bicep_curl']
        self.rep_count = 0
        self.stage = "down"

    def analyze(self, landmarks):
        result = {
            'angles': {},
            'feedback': [],
            'rep_count': self.rep_count,
            'stage': self.stage,
            'is_correct': True,
            'form_score': 100
        }

        angles = get_exercise_angles(landmarks, 'bicep_curl')
        result['angles'] = angles

        if not angles:
            return result

        # Analyze both arms
        for side in ['left', 'right']:
            elbow_key = f'{side}_elbow'
            shoulder_key = f'{side}_shoulder'

            if elbow_key in angles:
                elbow_angle = angles[elbow_key]

                # Rep counting (use the more visible arm)
                self._count_reps(elbow_angle)
                result['rep_count'] = self.rep_count
                result['stage'] = self.stage

                # Check shoulder movement (swinging)
                if shoulder_key in angles:
                    if angles[shoulder_key] > 40:
                        result['feedback'].append(
                            (f"{side.title()}: Don't swing! Pin elbow.", (0, 0, 255))
                        )
                        result['is_correct'] = False
                        result['form_score'] -= 20

        if result['is_correct']:
            if self.stage == 'up':
                result['feedback'].append(("Good curl! Lower slowly.", (0, 255, 0)))
            else:
                result['feedback'].append(("Good form! Curl up.", (0, 255, 0)))

        result['form_score'] = max(0, result['form_score'])
        return result

    def _count_reps(self, elbow_angle):
        up_threshold = self.thresholds['elbow_angle_up']
        down_threshold = self.thresholds['elbow_angle_down']

        if elbow_angle < up_threshold:
            if self.stage == 'down':
                self.rep_count += 1
            self.stage = 'up'
        elif elbow_angle > down_threshold:
            self.stage = 'down'

    def reset(self):
        self.rep_count = 0
        self.stage = "down"
