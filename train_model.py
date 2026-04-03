"""
train_model.py - Train ML models for posture classification
Uses collected pose data to train classifiers
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from config import (
    COLLECTED_DATA_DIR, PROCESSED_DATA_DIR,
    MODELS_DIR, TEST_SIZE, RANDOM_STATE
)


class PostureModelTrainer:
    """Train machine learning models for posture classification."""

    def __init__(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    def load_data(self, exercise_type):
        """Load all collected CSV data for a specific exercise."""
        pattern = os.path.join(COLLECTED_DATA_DIR, f"{exercise_type}_data_*.csv")
        files = glob.glob(pattern)

        if not files:
            print(f"No data files found for {exercise_type}")
            return None

        dataframes = []
        for file in files:
            df = pd.read_csv(file)
            dataframes.append(df)
            print(f"  Loaded {len(df)} samples from {os.path.basename(file)}")

        combined_df = pd.concat(dataframes, ignore_index=True)
        print(f"\nTotal samples: {len(combined_df)}")
        print(f"Label distribution:\n{combined_df['label'].value_counts()}")

        return combined_df

    def generate_synthetic_data(self, exercise_type, samples_per_class=500):
        """Generate synthetic training data based on angle thresholds."""
        print(f"\nGenerating synthetic data for {exercise_type}...")

        data = []

        if exercise_type == 'squat':
            for _ in range(samples_per_class):
                left_knee = np.random.uniform(75, 95)
                right_knee = left_knee + np.random.uniform(-5, 5)
                left_hip = np.random.uniform(65, 95)
                right_hip = left_hip + np.random.uniform(-5, 5)
                back_angle = np.random.uniform(155, 175)
                data.append([left_knee, right_knee, left_hip, right_hip, back_angle, 'correct'])

            for _ in range(samples_per_class // 3):
                left_knee = np.random.uniform(110, 160)
                right_knee = left_knee + np.random.uniform(-5, 5)
                left_hip = np.random.uniform(110, 160)
                right_hip = left_hip + np.random.uniform(-5, 5)
                back_angle = np.random.uniform(155, 175)
                data.append([left_knee, right_knee, left_hip, right_hip, back_angle, 'incorrect'])

            for _ in range(samples_per_class // 3):
                left_knee = np.random.uniform(30, 65)
                right_knee = left_knee + np.random.uniform(-5, 5)
                left_hip = np.random.uniform(30, 55)
                right_hip = left_hip + np.random.uniform(-5, 5)
                back_angle = np.random.uniform(155, 175)
                data.append([left_knee, right_knee, left_hip, right_hip, back_angle, 'incorrect'])

            for _ in range(samples_per_class // 3):
                left_knee = np.random.uniform(70, 100)
                right_knee = left_knee + np.random.uniform(-5, 5)
                left_hip = np.random.uniform(60, 100)
                right_hip = left_hip + np.random.uniform(-5, 5)
                back_angle = np.random.uniform(100, 145)
                data.append([left_knee, right_knee, left_hip, right_hip, back_angle, 'incorrect'])

            columns = ['left_knee_angle', 'right_knee_angle',
                       'left_hip_angle', 'right_hip_angle', 'back_angle', 'label']

        elif exercise_type == 'pushup':
            for _ in range(samples_per_class):
                left_elbow = np.random.uniform(80, 100)
                right_elbow = left_elbow + np.random.uniform(-5, 5)
                left_body = np.random.uniform(165, 180)
                right_body = left_body + np.random.uniform(-3, 3)
                data.append([left_elbow, right_elbow, left_body, right_body, 'correct'])

            for _ in range(samples_per_class // 2):
                left_elbow = np.random.uniform(80, 100)
                right_elbow = left_elbow + np.random.uniform(-5, 5)
                left_body = np.random.uniform(120, 155)
                right_body = left_body + np.random.uniform(-3, 3)
                data.append([left_elbow, right_elbow, left_body, right_body, 'incorrect'])

            for _ in range(samples_per_class // 2):
                left_elbow = np.random.uniform(130, 170)
                right_elbow = left_elbow + np.random.uniform(-5, 5)
                left_body = np.random.uniform(165, 180)
                right_body = left_body + np.random.uniform(-3, 3)
                data.append([left_elbow, right_elbow, left_body, right_body, 'incorrect'])

            columns = ['left_elbow_angle', 'right_elbow_angle',
                       'left_body_angle', 'right_body_angle', 'label']

        elif exercise_type == 'bicep_curl':
            for _ in range(samples_per_class):
                left_elbow = np.random.uniform(30, 50)
                right_elbow = left_elbow + np.random.uniform(-5, 5)
                left_shoulder = np.random.uniform(5, 20)
                right_shoulder = left_shoulder + np.random.uniform(-3, 3)
                data.append([left_elbow, right_elbow, left_shoulder, right_shoulder, 'correct'])

            for _ in range(samples_per_class):
                left_elbow = np.random.uniform(30, 100)
                right_elbow = left_elbow + np.random.uniform(-10, 10)
                left_shoulder = np.random.uniform(30, 60)
                right_shoulder = left_shoulder + np.random.uniform(-5, 5)
                data.append([left_elbow, right_elbow, left_shoulder, right_shoulder, 'incorrect'])

            columns = ['left_elbow_angle', 'right_elbow_angle',
                       'left_shoulder_angle', 'right_shoulder_angle', 'label']

        elif exercise_type == 'lunge':
            # Correct lunges: front knee ~90°, hip angles okay
            for _ in range(samples_per_class):
                left_knee = np.random.uniform(80, 100)
                right_knee = left_knee + np.random.uniform(30, 60)  # back leg straighter
                left_hip = np.random.uniform(160, 178)
                data.append([left_knee, right_knee, left_hip, 'correct'])

            # Incorrect: knee too far forward
            for _ in range(samples_per_class // 2):
                left_knee = np.random.uniform(40, 65)
                right_knee = left_knee + np.random.uniform(30, 60)
                left_hip = np.random.uniform(160, 178)
                data.append([left_knee, right_knee, left_hip, 'incorrect'])

            # Incorrect: torso leaning
            for _ in range(samples_per_class // 2):
                left_knee = np.random.uniform(80, 100)
                right_knee = left_knee + np.random.uniform(30, 60)
                left_hip = np.random.uniform(110, 150)
                data.append([left_knee, right_knee, left_hip, 'incorrect'])

            columns = ['left_knee_angle', 'right_knee_angle', 'left_hip_angle', 'label']

        elif exercise_type == 'shoulder_press':
            # Correct: full extension overhead
            for _ in range(samples_per_class):
                left_elbow = np.random.uniform(160, 178)
                right_elbow = left_elbow + np.random.uniform(-5, 5)
                left_shoulder = np.random.uniform(160, 178)
                right_shoulder = left_shoulder + np.random.uniform(-5, 5)
                data.append([left_elbow, right_elbow, left_shoulder, right_shoulder, 'correct'])

            # Incorrect: not fully extended
            for _ in range(samples_per_class // 2):
                left_elbow = np.random.uniform(90, 140)
                right_elbow = left_elbow + np.random.uniform(-5, 5)
                left_shoulder = np.random.uniform(90, 140)
                right_shoulder = left_shoulder + np.random.uniform(-5, 5)
                data.append([left_elbow, right_elbow, left_shoulder, right_shoulder, 'incorrect'])

            # Incorrect: asymmetric shoulders
            for _ in range(samples_per_class // 2):
                left_elbow = np.random.uniform(155, 175)
                right_elbow = left_elbow + np.random.uniform(-5, 5)
                left_shoulder = np.random.uniform(160, 178)
                right_shoulder = left_shoulder + np.random.uniform(15, 30)
                data.append([left_elbow, right_elbow, left_shoulder, right_shoulder, 'incorrect'])

            columns = ['left_elbow_angle', 'right_elbow_angle',
                        'left_shoulder_angle', 'right_shoulder_angle', 'label']

        else:
            # Fallback for unknown exercises
            for _ in range(samples_per_class):
                angles = [np.random.uniform(75, 95) for _ in range(4)]
                angles.append(np.random.uniform(155, 175))
                angles.append('correct')
                data.append(angles)

            for _ in range(samples_per_class):
                angles = [np.random.uniform(20, 60) for _ in range(4)]
                angles.append(np.random.uniform(100, 145))
                angles.append('incorrect')
                data.append(angles)

            columns = ['angle_1', 'angle_2', 'angle_3', 'angle_4', 'angle_5', 'label']

        df = pd.DataFrame(data, columns=columns)

        filepath = os.path.join(PROCESSED_DATA_DIR, f"{exercise_type}_synthetic.csv")
        df.to_csv(filepath, index=False)
        print(f"Generated {len(df)} synthetic samples -> {filepath}")

        return df

    def train_model(self, exercise_type, use_synthetic=True):
        """Train a posture classification model."""
        print(f"\n{'='*60}")
        print(f" TRAINING MODEL FOR: {exercise_type.upper()}")
        print(f"{'='*60}")

        df = self.load_data(exercise_type)

        if df is None or len(df) < 50:
            if use_synthetic:
                print("Using synthetic data for training...")
                df = self.generate_synthetic_data(exercise_type)
            else:
                print("Not enough data for training!")
                return None

        label_column = 'label'
        feature_columns = [col for col in df.columns
                           if col not in [label_column, 'exercise_stage']
                           and 'angle' in col.lower()]

        if not feature_columns:
            feature_columns = [col for col in df.columns
                               if col not in [label_column, 'exercise_stage']
                               and df[col].dtype in ['float64', 'int64']]

        print(f"\nFeatures: {feature_columns}")

        X = df[feature_columns].values
        y = df[label_column].values

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=TEST_SIZE, random_state=RANDOM_STATE,
            stratify=y_encoded
        )

        print(f"Training: {len(X_train)} | Testing: {len(X_test)}")

        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100, random_state=RANDOM_STATE, max_depth=10),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100, random_state=RANDOM_STATE, max_depth=5),
            'SVM': SVC(kernel='rbf', probability=True, random_state=RANDOM_STATE)
        }

        best_model = None
        best_accuracy = 0
        best_model_name = ""

        for name, model in models.items():
            print(f"\n--- Training {name} ---")

            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', model)
            ])

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            print(f"Accuracy: {accuracy:.4f}")
            print(classification_report(y_test, y_pred, target_names=le.classes_))

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = pipeline
                best_model_name = name

        print(f"\nBest Model: {best_model_name} - Accuracy: {best_accuracy:.4f}")

        model_path = os.path.join(MODELS_DIR, f"{exercise_type}_model.pkl")
        le_path = os.path.join(MODELS_DIR, f"{exercise_type}_label_encoder.pkl")
        features_path = os.path.join(MODELS_DIR, f"{exercise_type}_features.pkl")

        joblib.dump(best_model, model_path)
        joblib.dump(le, le_path)
        joblib.dump(feature_columns, features_path)

        print(f"Model saved: {model_path}")

        self._plot_confusion_matrix(y_test, best_model.predict(X_test),
                                    le.classes_, exercise_type)

        return best_model

    def _plot_confusion_matrix(self, y_true, y_pred, classes, exercise_type):
        """Generate and save confusion matrix plot."""
        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=classes, yticklabels=classes)
        plt.title(f'Confusion Matrix - {exercise_type.title()}')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()

        plot_path = os.path.join(MODELS_DIR, f"{exercise_type}_confusion_matrix.png")
        plt.savefig(plot_path)
        plt.close()
        print(f"Confusion matrix saved: {plot_path}")

    def train_all_exercises(self):
        """Train models for all supported exercises."""
        from config import SUPPORTED_EXERCISES
        for exercise in SUPPORTED_EXERCISES:
            self.train_model(exercise, use_synthetic=True)
            print()


class PosturePredictor:
    """Load trained models and make predictions."""

    def __init__(self, exercise_type):
        self.exercise_type = exercise_type
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        """Load the trained model for the exercise type."""
        model_path = os.path.join(MODELS_DIR, f"{self.exercise_type}_model.pkl")
        le_path = os.path.join(MODELS_DIR, f"{self.exercise_type}_label_encoder.pkl")
        features_path = os.path.join(MODELS_DIR, f"{self.exercise_type}_features.pkl")

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.label_encoder = joblib.load(le_path)
            self.feature_names = joblib.load(features_path)
            print(f"Loaded model for {self.exercise_type}")
            return True
        else:
            print(f"No trained model found for {self.exercise_type}")
            return False

    def predict(self, angles):
        """
        Predict posture correctness.

        Returns:
            tuple: (prediction_label, confidence)
        """
        if self.model is None:
            return "unknown", 0.0

        features = []
        for fname in self.feature_names:
            features.append(angles.get(fname, 0))

        features = np.array(features).reshape(1, -1)

        prediction = self.model.predict(features)[0]
        label = self.label_encoder.inverse_transform([prediction])[0]

        if hasattr(self.model.named_steps['classifier'], 'predict_proba'):
            proba = self.model.predict_proba(features)[0]
            confidence = max(proba)
        else:
            confidence = 1.0

        return label, confidence


if __name__ == "__main__":
    trainer = PostureModelTrainer()

    print("="*60)
    print(" POSTURE MODEL TRAINER")
    print("="*60)
    print("\nOptions:")
    print(" 1. Train model for specific exercise")
    print(" 2. Train models for all exercises")
    print(" 3. Generate synthetic data only")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == '1':
        print("\nAvailable exercises:")
        from config import SUPPORTED_EXERCISES
        for i, ex in enumerate(SUPPORTED_EXERCISES, 1):
            print(f"  {i}. {ex}")
        ex_choice = int(input("Select exercise number: ")) - 1
        exercise = SUPPORTED_EXERCISES[ex_choice]
        trainer.train_model(exercise, use_synthetic=True)

    elif choice == '2':
        trainer.train_all_exercises()

    elif choice == '3':
        from config import SUPPORTED_EXERCISES
        for exercise in SUPPORTED_EXERCISES:
            trainer.generate_synthetic_data(exercise)
