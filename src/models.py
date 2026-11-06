"""
Machine Learning & Spatial Risk Modeling Engine
Route-Wise Traffic Accident Risk Prediction System
Course: 213CSE2301 - Predictive Analytics (Autonomy)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.inspection import permutation_importance


class AccidentRiskModel:
    def __init__(self, n_clusters: int = 20, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.rf_model = None
        self.comparison_models = {}
        self.le_time = LabelEncoder()
        self.le_weather = LabelEncoder()
        self.le_road = LabelEncoder()
        self.le_target = LabelEncoder()
        self.cluster_risk_df = None
        self.metadata = {}
        self.feature_names = [
            'Hour', 'Time_Cat_Encoded', 'Weather_Cat_Encoded',
            'Road_Cat_Encoded', 'Cluster_Risk_Score'
        ]

    def fit_spatial_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fits K-Means on Latitude & Longitude to detect accident hotspots."""
        df = df.copy()
        df['Cluster'] = self.kmeans.fit_predict(df[['Latitude', 'Longitude']])

        # Compute mean severity score per cluster
        sev_score_map = {'Low': 1.0, 'Medium': 2.0, 'High': 3.0}
        df['Severity_Score'] = df['Severity'].map(sev_score_map).fillna(1.5)

        cluster_risk = df.groupby('Cluster')['Severity_Score'].mean().reset_index()
        cluster_risk.rename(columns={'Severity_Score': 'Cluster_Risk_Score'}, inplace=True)
        self.cluster_risk_df = cluster_risk

        df = df.merge(cluster_risk, on='Cluster', how='left')
        return df

    def get_cluster_risk_score(self, lat: float, lon: float) -> float:
        """Finds nearest cluster hotspot and returns its baseline risk score."""
        cluster_id = self.kmeans.predict(pd.DataFrame([[lat, lon]], columns=["Latitude", "Longitude"]))[0]
        match = self.cluster_risk_df[self.cluster_risk_df['Cluster'] == cluster_id]
        if not match.empty:
            return float(match['Cluster_Risk_Score'].values[0])
        return 1.5

    def prepare_features(self, df: pd.DataFrame, is_training: bool = True) -> tuple:
        """Encodes features and extracts X, y matrices."""
        df = df.copy()
        if 'Cluster_Risk_Score' not in df.columns:
            df = self.fit_spatial_clusters(df)

        if is_training:
            self.le_time.fit(df['Time_Category'])
            self.le_weather.fit(df['Weather'])
            self.le_road.fit(df['Road_Type'])
            self.le_target.fit(df['Severity'])

        df['Time_Cat_Encoded'] = self.le_time.transform(df['Time_Category'])
        df['Weather_Cat_Encoded'] = self.le_weather.transform(df['Weather'])
        df['Road_Cat_Encoded'] = self.le_road.transform(df['Road_Type'])

        X = df[self.feature_names]
        y = self.le_target.transform(df['Severity']) if 'Severity' in df.columns else None
        return X, y, df

    def train_models(self, df: pd.DataFrame, test_size: float = 0.2):
        """Trains Random Forest alongside comparative algorithms."""
        X, y, df_processed = self.prepare_features(df, is_training=True)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )

        # Primary Model: Random Forest Classifier
        # Tuned with class weighting & depth to balance accuracy and generalization
        self.rf_model = RandomForestClassifier(
            n_estimators=120,
            max_depth=9,
            min_samples_split=4,
            random_state=self.random_state,
            class_weight='balanced'
        )
        self.rf_model.fit(X_train, y_train)

        # Fit comparative models from Course Syllabus
        lr = LogisticRegression(max_iter=1000, random_state=self.random_state)
        lr.fit(X_train, y_train)

        dt = DecisionTreeClassifier(max_depth=8, criterion='entropy', random_state=self.random_state)
        dt.fit(X_train, y_train)

        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(X_train, y_train)

        nb = GaussianNB()
        nb.fit(X_train, y_train)

        svm = SVC(kernel='rbf', probability=True, random_state=self.random_state)
        svm.fit(X_train, y_train)

        self.comparison_models = {
            'Random Forest': self.rf_model,
            'Logistic Regression': lr,
            'Decision Tree (ID3)': dt,
            'k-Nearest Neighbors (k-NN)': knn,
            'Naive Bayes (Gaussian)': nb,
            'Support Vector Machine (SVM)': svm
        }

        # Evaluate all models
        eval_results = {}
        for name, model in self.comparison_models.items():
            y_pred = model.predict(X_test)
            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
            rec = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
            f1 = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
            eval_results[name] = {
                'Accuracy': round(acc, 4),
                'Precision': round(prec, 4),
                'Recall': round(rec, 4),
                'F1_Score': round(f1, 4)
            }

        # RF Details
        y_pred_rf = self.rf_model.predict(X_test)
        classes = list(self.le_target.classes_)  # ['High', 'Low', 'Medium']
        cm = confusion_matrix(y_test, y_pred_rf)

        # Permutation Importance
        perm_imp = permutation_importance(
            self.rf_model, X_test, y_test, n_repeats=5, random_state=self.random_state
        )

        self.metadata = {
            'target_classes': classes,
            'feature_names': self.feature_names,
            'train_records': len(X_train),
            'test_records': len(X_test),
            'total_records': len(df),
            'model_comparisons': eval_results,
            'rf_metrics': eval_results['Random Forest'],
            'confusion_matrix': cm.tolist(),
            'feature_importances': dict(zip(self.feature_names, [float(v) for v in self.rf_model.feature_importances_])),
            'permutation_importances': dict(zip(self.feature_names, [float(v) for v in perm_imp.importances_mean]))
        }

        return eval_results, cm, self.metadata

    def predict_risk(self, lat: float, lon: float, hour: int, time_cat: str, weather: str, road_type: str) -> dict:
        """
        Predicts accident risk level, class probabilities, and spatial risk score.
        """
        cluster_score = self.get_cluster_risk_score(lat, lon)

        try:
            t_enc = self.le_time.transform([time_cat])[0]
        except Exception:
            t_enc = 0

        try:
            w_enc = self.le_weather.transform([weather])[0]
        except Exception:
            w_enc = 0

        try:
            r_enc = self.le_road.transform([road_type])[0]
        except Exception:
            r_enc = 0

        features_df = pd.DataFrame([[hour, t_enc, w_enc, r_enc, cluster_score]], columns=self.feature_names)
        pred_idx = self.rf_model.predict(features_df)[0]
        probs = self.rf_model.predict_proba(features_df)[0]
        classes = list(self.le_target.classes_)

        predicted_class = classes[pred_idx]
        prob_dict = {classes[i]: round(float(probs[i]), 4) for i in range(len(classes))}

        # Calculate composite risk index (0.0 to 1.0)
        # Weights: High = 1.0, Medium = 0.5, Low = 0.1
        composite_risk = (
            prob_dict.get('High', 0.0) * 1.0 +
            prob_dict.get('Medium', 0.0) * 0.5 +
            prob_dict.get('Low', 0.0) * 0.1
        )

        return {
            'predicted_severity': predicted_class,
            'confidence': round(float(np.max(probs)), 4),
            'class_probabilities': prob_dict,
            'cluster_risk_score': round(cluster_score, 2),
            'composite_risk_score': round(composite_risk, 4)
        }

    def predict_batch_risk(self, lats: List[float], lons: List[float], hour: int, time_cat: str, weather: str, road_type: str) -> List[dict]:
        """High-performance vectorized prediction for route nodes."""
        n = len(lats)
        if n == 0:
            return []

        coords_df = pd.DataFrame(np.column_stack([lats, lons]), columns=['Latitude', 'Longitude'])
        cluster_ids = self.kmeans.predict(coords_df)

        risk_map = dict(zip(self.cluster_risk_df['Cluster'], self.cluster_risk_df['Cluster_Risk_Score']))
        cluster_scores = np.array([risk_map.get(cid, 1.5) for cid in cluster_ids])

        try:
            t_enc = self.le_time.transform([time_cat])[0]
        except Exception:
            t_enc = 0

        try:
            w_enc = self.le_weather.transform([weather])[0]
        except Exception:
            w_enc = 0

        try:
            r_enc = self.le_road.transform([road_type])[0]
        except Exception:
            r_enc = 0

        features = pd.DataFrame(
            np.column_stack([
                np.full(n, hour),
                np.full(n, t_enc),
                np.full(n, w_enc),
                np.full(n, r_enc),
                cluster_scores
            ]),
            columns=self.feature_names
        )

        probs_all = self.rf_model.predict_proba(features)
        pred_indices = np.argmax(probs_all, axis=1)
        classes = list(self.le_target.classes_)

        high_idx = classes.index('High') if 'High' in classes else -1
        med_idx = classes.index('Medium') if 'Medium' in classes else -1
        low_idx = classes.index('Low') if 'Low' in classes else -1

        results = []
        for i in range(n):
            probs = probs_all[i]
            pred_class = classes[pred_indices[i]]
            prob_dict = {classes[c]: round(float(probs[c]), 4) for c in range(len(classes))}

            p_high = float(probs[high_idx]) if high_idx >= 0 else 0.0
            p_med = float(probs[med_idx]) if med_idx >= 0 else 0.0
            p_low = float(probs[low_idx]) if low_idx >= 0 else 0.0
            comp = p_high * 1.0 + p_med * 0.5 + p_low * 0.1

            results.append({
                'lat': lats[i],
                'lon': lons[i],
                'severity': pred_class,
                'confidence': round(float(probs[pred_indices[i]]), 4),
                'class_probabilities': prob_dict,
                'cluster_score': round(float(cluster_scores[i]), 2),
                'composite_score': round(float(comp), 4)
            })
        return results

    def save_artifacts(self, output_dir: str = 'models'):
        os.makedirs(output_dir, exist_ok=True)
        joblib.dump(self.rf_model, os.path.join(output_dir, 'rf_model.pkl'))
        joblib.dump(self.kmeans, os.path.join(output_dir, 'kmeans_model.pkl'))
        joblib.dump(self.cluster_risk_df, os.path.join(output_dir, 'cluster_risk_df.pkl'))
        encoders = {
            'le_time': self.le_time,
            'le_weather': self.le_weather,
            'le_road': self.le_road,
            'le_target': self.le_target
        }
        joblib.dump(encoders, os.path.join(output_dir, 'encoders.pkl'))
        with open(os.path.join(output_dir, 'model_metadata.json'), 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f" Saved model artifacts to {output_dir}/")

    def load_artifacts(self, model_dir: str = 'models'):
        self.rf_model = joblib.load(os.path.join(model_dir, 'rf_model.pkl'))
        self.kmeans = joblib.load(os.path.join(model_dir, 'kmeans_model.pkl'))
        self.cluster_risk_df = joblib.load(os.path.join(model_dir, 'cluster_risk_df.pkl'))
        encoders = joblib.load(os.path.join(model_dir, 'encoders.pkl'))
        self.le_time = encoders['le_time']
        self.le_weather = encoders['le_weather']
        self.le_road = encoders['le_road']
        self.le_target = encoders['le_target']
        meta_path = os.path.join(model_dir, 'model_metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                self.metadata = json.load(f)
        print(f" Loaded model artifacts from {model_dir}/")


def train_and_save(data_path: str = 'data/cleaned_accidents_6469.csv', output_dir: str = 'models'):
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    model = AccidentRiskModel(n_clusters=20, random_state=42)
    eval_results, cm, meta = model.train_models(df)

    print("\n" + "="*50)
    print("MODEL EVALUATION COMPARISON (COURSE 213CSE2301)")
    print("="*50)
    print(pd.DataFrame(eval_results).T.to_string())

    print("\nConfusion Matrix (Random Forest):")
    print(f"Target Classes: {meta['target_classes']}")
    print(np.array(cm))

    model.save_artifacts(output_dir)
    return model


if __name__ == '__main__':
    train_and_save()
