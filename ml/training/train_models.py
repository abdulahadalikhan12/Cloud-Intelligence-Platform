import pandas as pd
import numpy as np
import joblib
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ml.preprocessing import clean_data, engineer_features
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb

MODELS_DIR = "ml/models"
os.makedirs(MODELS_DIR, exist_ok=True)

def train_classification(df):
    print("\n--- Training Classification Models (Risk Prediction) ---")
    features = ['temperature', 'humidity', 'rain', 'pressure', 'wind_speed', 'month', 'hour']
    target = 'aqi_category'
    
    X = df[features]
    y = df[target]
    
    # Label encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    joblib.dump(le, f"{MODELS_DIR}/classification_label_encoder.pkl")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    # Scale features (Critical for Logistic Regression & linear models)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    joblib.dump(scaler, f"{MODELS_DIR}/classification_scaler.pkl")
    
    # Logistic Regression
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    print(f"Logistic Regression Accuracy: {accuracy_score(y_test, y_pred_lr):.4f}")
    joblib.dump(lr, f"{MODELS_DIR}/risk_logistic_regression.pkl")
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    print(f"Random Forest Accuracy: {accuracy_score(y_test, y_pred_rf):.4f}")
    joblib.dump(rf, f"{MODELS_DIR}/risk_random_forest.pkl")

    # XGBoost
    xgb_clf = xgb.XGBClassifier(eval_metric='mlogloss', random_state=42)
    xgb_clf.fit(X_train, y_train)
    y_pred_xgb = xgb_clf.predict(X_test)
    print(f"XGBoost Accuracy: {accuracy_score(y_test, y_pred_xgb):.4f}")
    joblib.dump(xgb_clf, f"{MODELS_DIR}/risk_xgboost.pkl")

def train_regression(df):
    print("\n--- Training Regression Models (PM2.5 Prediction) ---")
    features = ['temperature', 'humidity', 'rain', 'pressure', 'wind_speed', 'month', 'hour']
    target = 'pm2_5'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    joblib.dump(scaler, f"{MODELS_DIR}/regression_scaler.pkl")
    
    # Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    mse_lr = mean_squared_error(y_test, y_pred_lr)
    print(f"Linear Regression RMSE: {np.sqrt(mse_lr):.4f}")
    joblib.dump(lr, f"{MODELS_DIR}/pollution_linear_reg.pkl")
    
    # Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    mse_rf = mean_squared_error(y_test, y_pred_rf)
    print(f"Random Forest RMSE: {np.sqrt(mse_rf):.4f}")
    joblib.dump(rf, f"{MODELS_DIR}/pollution_random_forest.pkl")

    # XGBoost Regressor
    xgb_reg = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    xgb_reg.fit(X_train, y_train)
    y_pred_xgb = xgb_reg.predict(X_test)
    mse_xgb = mean_squared_error(y_test, y_pred_xgb)
    print(f"XGBoost RMSE: {np.sqrt(mse_xgb):.4f}")
    joblib.dump(xgb_reg, f"{MODELS_DIR}/pollution_xgboost.pkl")

def train_clustering(df):
    print("\n--- Training Clustering & PCA (City Segmentation) ---")
    # Group by city to get average profile
    city_profiles = df.groupby('city')[['temperature', 'humidity', 'rain', 'pm2_5']].mean()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(city_profiles)
    joblib.dump(scaler, f"{MODELS_DIR}/clustering_scaler.pkl")
    
    # PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    joblib.dump(pca, f"{MODELS_DIR}/pca_model.pkl")
    
    # KMeans
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(X_scaled)
    # city_profiles['cluster'] = kmeans.labels_
    # print(city_profiles)
    joblib.dump(kmeans, f"{MODELS_DIR}/kmeans_model.pkl")

def main():
    data_path = "data/raw_climate_data.csv"
    if not os.path.exists(data_path):
        print("Data not found. Please run ingestion first.")
        return

    df = pd.read_csv(data_path)
    df = clean_data(df)
    df = engineer_features(df)
    
    train_classification(df)
    train_regression(df)
    train_clustering(df)
    
    print("\nAll models trained and saved.")

if __name__ == "__main__":
    main()
