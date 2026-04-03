"""
lunge_analyzer.py - Lunge exercise posture analyzer
"""
from utils.angle_calculator import AngleCalculator, get_exercise_angles
from config import EXERCISE_THRESHOLDS


class LungeAnalyzer:
    """Analyzes lunge posture and provides feedback."""

    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.thresholds = EXERCISE_THRESHOLDS['lunge']
        self.rep_count = 0
        self.stage = "standing"

    def analyze(self, landmarks):
        result = {
            'angles': {},
            'feedback': [],
            'rep_count': self.rep_count,
            'stage': self.stage,
            'is_correct': True,
            'form_score': 100
        }

        angles = get_exercise_angles(landmarks, 'lunge')
        result['angles'] = angles

        if not angles:
            return result

        knee_angles = []
        if 'left_knee' in angles:
            knee_angles.append(angles['left_knee'])
        if 'right_knee' in angles:
            knee_angles.append(angles['right_knee'])

        if knee_angles:
            front_knee = min(knee_angles)

            # Count reps
            if front_knee > 150:
                if self.stage == 'down':
                    self.rep_count += 1
                self.stage = 'standing'
            elif front_knee < 120:
                self.stage = 'down'

            result['rep_count'] = self.rep_count
            result['stage'] = self.stage

            tolerance = self.thresholds.get('tolerance', 20)
            target = self.thresholds['front_knee_angle']

            if self.stage == 'down':
                if front_knee < target - tolerance:
                    result['feedback'].append(("Knee too far forward!", (0, 0, 255)))
                    result['is_correct'] = False
                    result['form_score'] -= 25
                elif front_knee > target + tolerance:
                    result['feedback'].append(("Lunge deeper!", (0, 165, 255)))
                    result['form_score'] -= 15
                else:
                    result['feedback'].append(("Perfect lunge depth!", (0, 255, 0)))

            # Check torso
            if 'left_hip' in angles:
                if angles['left_hip'] < self.thresholds.get('torso_angle_min', 160):
                    result['feedback'].append(("Keep torso upright!", (0, 0, 255)))
                    result['is_correct'] = False
                    result['form_score'] -= 20

        result['form_score'] = max(0, result['form_score'])
        return result

    def reset(self):
        self.rep_count = 0
        self.stage = "standing"
