"""
shoulder_press_analyzer.py - Shoulder press exercise posture analyzer
"""
from utils.angle_calculator import AngleCalculator, get_exercise_angles
from config import EXERCISE_THRESHOLDS


class ShoulderPressAnalyzer:
    """Analyzes shoulder press posture and provides feedback."""

    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.thresholds = EXERCISE_THRESHOLDS['shoulder_press']
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

        form_score = 100

        angles = get_exercise_angles(landmarks, 'shoulder_press')
        result['angles'] = angles

        if not angles:
            return result

        elbow_angle = None
        if 'left_elbow' in angles and 'right_elbow' in angles:
            elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
        elif 'left_elbow' in angles:
            elbow_angle = angles['left_elbow']

        if elbow_angle is not None:
            up_threshold = self.thresholds['elbow_angle_up']
            down_threshold = self.thresholds['elbow_angle_down']

            if elbow_angle > up_threshold:
                if self.stage == 'down':
                    self.rep_count += 1
                self.stage = 'up'
                result['feedback'].append(("Full extension! Lower down.", (0, 255, 0)))
            elif elbow_angle < down_threshold:
                self.stage = 'down'
                result['feedback'].append(("Press up!", (255, 255, 0)))
            else:
                result['feedback'].append(("Keep pressing to full extension!", (0, 165, 255)))
                form_score -= 15

        # Check shoulder symmetry
        if 'left_shoulder' in angles and 'right_shoulder' in angles:
            diff = abs(angles['left_shoulder'] - angles['right_shoulder'])
            if diff > self.thresholds.get('shoulder_alignment', 10):
                result['feedback'].append(("Keep shoulders even!", (0, 0, 255)))
                result['is_correct'] = False
                form_score -= 20

        result['rep_count'] = self.rep_count
        result['stage'] = self.stage
        result['form_score'] = max(0, form_score)

        return result

    def reset(self):
        self.rep_count = 0
        self.stage = "down"
