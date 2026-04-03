"""
angle_calculator.py - Joint Angle Calculation Utilities
Calculates angles between body joints for posture analysis
"""
import numpy as np
import math


class AngleCalculator:
    """
    Calculate angles between three body landmarks.
    This is the core of posture analysis.
    """

    @staticmethod
    def calculate_angle(point_a, point_b, point_c):
        """
        Calculate the angle at point_b formed by points A-B-C.

        For example, to calculate elbow angle:
          - point_a = shoulder
          - point_b = elbow (vertex)
          - point_c = wrist

        Args:
            point_a: (x, y) or (x, y, z) tuple for first point
            point_b: (x, y) or (x, y, z) tuple for vertex point
            point_c: (x, y) or (x, y, z) tuple for third point

        Returns:
            float: Angle in degrees (0-180)
        """
        a = np.array(point_a[:2])
        b = np.array(point_b[:2])
        c = np.array(point_c[:2])

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cosine_angle))

        return round(angle, 2)

    @staticmethod
    def calculate_angle_3d(point_a, point_b, point_c):
        """Calculate 3D angle at point_b formed by points A-B-C."""
        a = np.array(point_a[:3])
        b = np.array(point_b[:3])
        c = np.array(point_c[:3])

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cosine_angle))

        return round(angle, 2)

    @staticmethod
    def calculate_distance(point_a, point_b):
        """Calculate Euclidean distance between two points."""
        a = np.array(point_a[:2])
        b = np.array(point_b[:2])
        return float(np.linalg.norm(a - b))

    @staticmethod
    def calculate_vertical_angle(point_a, point_b):
        """
        Calculate the angle of line AB with respect to vertical axis.
        Useful for checking if back/torso is straight.
        """
        dx = point_b[0] - point_a[0]
        dy = point_b[1] - point_a[1]
        angle = abs(math.degrees(math.atan2(dx, dy)))
        return round(angle, 2)

    @staticmethod
    def calculate_horizontal_angle(point_a, point_b):
        """
        Calculate the angle of line AB with respect to horizontal axis.
        Useful for checking shoulder alignment.
        """
        dx = point_b[0] - point_a[0]
        dy = point_b[1] - point_a[1]
        angle = abs(math.degrees(math.atan2(dy, dx)))
        return round(angle, 2)

    @staticmethod
    def is_angle_in_range(angle, min_angle, max_angle):
        """Check if an angle falls within a specified range."""
        return min_angle <= angle <= max_angle

    @staticmethod
    def get_angle_deviation(angle, target_angle, tolerance=15):
        """
        Calculate how far an angle deviates from a target.

        Returns:
            tuple: (deviation_amount, is_within_tolerance)
        """
        deviation = abs(angle - target_angle)
        within_tolerance = deviation <= tolerance
        return round(deviation, 2), within_tolerance


def get_exercise_angles(landmarks, exercise_type):
    """
    Calculate all relevant angles for a specific exercise.

    Args:
        landmarks: Dictionary of landmarks {id: (x, y, z, visibility)}
        exercise_type: Type of exercise ('squat', 'pushup', etc.)

    Returns:
        dict: Dictionary of calculated angles
    """
    if landmarks is None:
        return {}

    calc = AngleCalculator()
    angles = {}

    if exercise_type == 'squat':
        if all(k in landmarks for k in [23, 25, 27]):
            angles['left_knee'] = calc.calculate_angle(
                landmarks[23][:2], landmarks[25][:2], landmarks[27][:2]
            )
        if all(k in landmarks for k in [24, 26, 28]):
            angles['right_knee'] = calc.calculate_angle(
                landmarks[24][:2], landmarks[26][:2], landmarks[28][:2]
            )
        if all(k in landmarks for k in [11, 23, 25]):
            angles['left_hip'] = calc.calculate_angle(
                landmarks[11][:2], landmarks[23][:2], landmarks[25][:2]
            )
        if all(k in landmarks for k in [12, 24, 26]):
            angles['right_hip'] = calc.calculate_angle(
                landmarks[12][:2], landmarks[24][:2], landmarks[26][:2]
            )
        if all(k in landmarks for k in [7, 11, 23]):
            angles['left_back'] = calc.calculate_angle(
                landmarks[7][:2], landmarks[11][:2], landmarks[23][:2]
            )

    elif exercise_type == 'pushup':
        if all(k in landmarks for k in [11, 13, 15]):
            angles['left_elbow'] = calc.calculate_angle(
                landmarks[11][:2], landmarks[13][:2], landmarks[15][:2]
            )
        if all(k in landmarks for k in [12, 14, 16]):
            angles['right_elbow'] = calc.calculate_angle(
                landmarks[12][:2], landmarks[14][:2], landmarks[16][:2]
            )
        if all(k in landmarks for k in [11, 23, 27]):
            angles['left_body'] = calc.calculate_angle(
                landmarks[11][:2], landmarks[23][:2], landmarks[27][:2]
            )
        if all(k in landmarks for k in [12, 24, 28]):
            angles['right_body'] = calc.calculate_angle(
                landmarks[12][:2], landmarks[24][:2], landmarks[28][:2]
            )

    elif exercise_type == 'bicep_curl':
        if all(k in landmarks for k in [11, 13, 15]):
            angles['left_elbow'] = calc.calculate_angle(
                landmarks[11][:2], landmarks[13][:2], landmarks[15][:2]
            )
        if all(k in landmarks for k in [12, 14, 16]):
            angles['right_elbow'] = calc.calculate_angle(
                landmarks[12][:2], landmarks[14][:2], landmarks[16][:2]
            )
        if all(k in landmarks for k in [23, 11, 13]):
            angles['left_shoulder'] = calc.calculate_angle(
                landmarks[23][:2], landmarks[11][:2], landmarks[13][:2]
            )
        if all(k in landmarks for k in [24, 12, 14]):
            angles['right_shoulder'] = calc.calculate_angle(
                landmarks[24][:2], landmarks[12][:2], landmarks[14][:2]
            )

    elif exercise_type == 'lunge':
        if all(k in landmarks for k in [23, 25, 27]):
            angles['left_knee'] = calc.calculate_angle(
                landmarks[23][:2], landmarks[25][:2], landmarks[27][:2]
            )
        if all(k in landmarks for k in [24, 26, 28]):
            angles['right_knee'] = calc.calculate_angle(
                landmarks[24][:2], landmarks[26][:2], landmarks[28][:2]
            )
        if all(k in landmarks for k in [11, 23, 25]):
            angles['left_hip'] = calc.calculate_angle(
                landmarks[11][:2], landmarks[23][:2], landmarks[25][:2]
            )

    elif exercise_type == 'shoulder_press':
        if all(k in landmarks for k in [11, 13, 15]):
            angles['left_elbow'] = calc.calculate_angle(
                landmarks[11][:2], landmarks[13][:2], landmarks[15][:2]
            )
        if all(k in landmarks for k in [12, 14, 16]):
            angles['right_elbow'] = calc.calculate_angle(
                landmarks[12][:2], landmarks[14][:2], landmarks[16][:2]
            )
        if all(k in landmarks for k in [23, 11, 13]):
            angles['left_shoulder'] = calc.calculate_angle(
                landmarks[23][:2], landmarks[11][:2], landmarks[13][:2]
            )
        if all(k in landmarks for k in [24, 12, 14]):
            angles['right_shoulder'] = calc.calculate_angle(
                landmarks[24][:2], landmarks[12][:2], landmarks[14][:2]
            )

    return angles
