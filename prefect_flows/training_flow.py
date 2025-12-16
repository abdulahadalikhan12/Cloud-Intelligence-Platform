from prefect import flow, task
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ml.training.train_models import train_classification, train_regression, train_clustering, clean_data, engineer_features
import pandas as pd

@task(name="Load and Preprocess Data")
def load_and_preprocess_task():
    data_path = "data/raw_climate_data.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError("Data not found. Please run ingestion flow first.")
    
    df = pd.read_csv(data_path)
    df = clean_data(df)
    df = engineer_features(df)
    return df

@task(name="Train Classification Models")
def train_classification_task(df):
    train_classification(df)

@task(name="Train Regression Models")
def train_regression_task(df):
    train_regression(df)

@task(name="Train Clustering Models")
def train_clustering_task(df):
    train_clustering(df)

@flow(name="Model Training Pipeline")
def training_flow():
    df = load_and_preprocess_task()
    train_classification_task(df)
    train_regression_task(df)
    train_clustering_task(df)

if __name__ == "__main__":
    training_flow()
