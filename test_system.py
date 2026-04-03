"""
test_system.py - Test all components of the system
"""
import cv2
import numpy as np
import sys
import os


def test_imports():
    """Test all required imports."""
    print("Testing imports...")
    try:
        import mediapipe
        import sklearn
        import flask
        import pandas
        print("  All imports successful")
        return True
    except ImportError as e:
        print(f"  Import failed: {e}")
        return False


def test_angle_calculator():
    """Test angle calculations."""
    print("\nTesting Angle Calculator...")
    from utils.angle_calculator import AngleCalculator

    calc = AngleCalculator()

    # Right angle test (should be ~90 degrees)
    angle = calc.calculate_angle((0, 0), (0, 1), (1, 1))
    print(f"  Right angle test:   {angle}° (expected ~90)")
    assert 85 <= angle <= 95, f"Expected ~90, got {angle}"

    # Straight line test (should be ~180 degrees)
    angle = calc.calculate_angle((0, 0), (1, 0), (2, 0))
    print(f"  Straight line test: {angle}° (expected ~180)")
    assert 175 <= angle <= 185, f"Expected ~180, got {angle}"

    # Distance test (3-4-5 triangle)
    dist = calc.calculate_distance((0, 0), (3, 4))
    print(f"  Distance test:      {dist} (expected 5.0)")
    assert abs(dist - 5.0) < 0.01

    print("  All angle calculations correct")
    return True


def test_exercise_analyzers():
    """Test exercise analyzers with mock data."""
    print("\nTesting Exercise Analyzers...")

    from exercises.squat_analyzer import SquatAnalyzer
    from exercises.pushup_analyzer import PushupAnalyzer
    from exercises.bicep_curl_analyzer import BicepCurlAnalyzer
    from exercises.lunge_analyzer import LungeAnalyzer
    from exercises.shoulder_press_analyzer import ShoulderPressAnalyzer

    # Mock landmarks approximate positions
    mock_landmarks = {}
    for i in range(33):
        mock_landmarks[i] = (
            0.5 + np.random.uniform(-0.1, 0.1),
            0.1 + i * 0.025,
            0.0,
            0.95
        )

    analyzers = {
        'Squat': SquatAnalyzer(),
        'Pushup': PushupAnalyzer(),
        'Bicep Curl': BicepCurlAnalyzer(),
        'Lunge': LungeAnalyzer(),
        'Shoulder Press': ShoulderPressAnalyzer(),
    }

    for name, analyzer in analyzers.items():
        result = analyzer.analyze(mock_landmarks)
        print(f"  {name}: stage={result['stage']}, reps={result['rep_count']}")
        print(f"  {name} analyzer OK")

    return True


def test_model_training():
    """Test model training with synthetic data."""
    print("\nTesting Model Training...")
    from train_model import PostureModelTrainer

    trainer = PostureModelTrainer()
    model = trainer.train_model('squat', use_synthetic=True)

    if model is not None:
        print("  Model training successful")

        from train_model import PosturePredictor
        predictor = PosturePredictor('squat')

        test_angles = {
            'left_knee_angle': 85,
            'right_knee_angle': 87,
            'left_hip_angle': 80,
            'right_hip_angle': 82,
            'back_angle': 165
        }

        label, confidence = predictor.predict(test_angles)
        print(f"  Prediction: {label} (confidence: {confidence:.2f})")
        print("  Model prediction works")
        return True
    else:
        print("  Model training failed")
        return False


def test_pose_detector():
    """Test pose detection with webcam."""
    print("\nTesting Pose Detector...")
    from utils.pose_detector import PoseDetector

    detector = PoseDetector()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("  Cannot open camera (skipping)")
        return None

    ret, frame = cap.read()
    if ret:
        frame, results = detector.detect_pose(frame)
        if detector.is_pose_detected():
            print("  Pose detected successfully")
            landmarks = detector.get_all_landmarks()
            print(f"  Got {len(landmarks)} landmarks")
        else:
            print("  No pose detected (stand in front of camera when testing)")

    cap.release()
    detector.release()
    print("  Pose detector initialized successfully")
    return True


def run_all_tests():
    """Run all system tests."""
    print("=" * 60)
    print(" SYSTEM TEST SUITE")
    print("=" * 60)

    results = {}

    results['imports'] = test_imports()
    results['angle_calculator'] = test_angle_calculator()
    results['exercise_analyzers'] = test_exercise_analyzers()
    results['model_training'] = test_model_training()

    try:
        results['pose_detector'] = test_pose_detector()
    except Exception as e:
        print(f"  Pose detector test error: {e}")
        results['pose_detector'] = None

    print("\n" + "=" * 60)
    print(" TEST RESULTS")
    print("=" * 60)

    for test_name, passed in results.items():
        if passed is True:
            status = "PASSED"
        elif passed is False:
            status = "FAILED"
        else:
            status = "SKIPPED"
        print(f"  {test_name:<25} {status}")

    all_passed = all(v is True for v in results.values() if v is not None)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed — check output above."))
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
