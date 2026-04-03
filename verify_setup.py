"""
verify_setup.py - Verify all dependencies are installed correctly
"""
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import sklearn
import flask

print("=" * 50)
print(" INSTALLATION VERIFICATION")
print("=" * 50)

print(f"OpenCV version:      {cv2.__version__}")
print(f"MediaPipe version:   {mp.__version__}")
print(f"NumPy version:       {np.__version__}")
print(f"Pandas version:      {pd.__version__}")
print(f"Scikit-learn version:{sklearn.__version__}")
print(f"Flask version:       {flask.__version__}")

print("\nAll libraries installed successfully!")

# Test webcam
print("\nTesting webcam...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("Webcam is working!")
    cap.release()
else:
    print("Webcam not detected. Check your camera connection.")

print("=" * 50)
