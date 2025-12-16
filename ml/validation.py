import pandas as pd
from deepchecks.tabular import Dataset
from deepchecks.tabular.suites import data_integrity
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ml.preprocessing import clean_data

def run_data_validation():
    print("--- Running DeepChecks Data Validation ---")
    data_path = "data/raw_climate_data.csv"
    if not os.path.exists(data_path):
        print("Data not found. Please run ingestion first.")
        return

    # Load and prep data
    df = pd.read_csv(data_path)
    
    # We want to validate the raw-ish data before heavy feature engineering, 
    # but after basic cleaning (like duplicates) to avoid trivial errors.
    # Or we can validate RAW raw data. Let's validate df after clean_data.
    df = clean_data(df)

    # Define Dataset for DeepChecks
    # We treat 'temperature' as the target for regression checks, or we can just run data integrity.
    # Data Integrity Suite does not require a model or target necessarily, but specifying categorical features helps.
    ds = Dataset(df, cat_features=[], index_name='time')

    # Run Integrity Suite
    integ_suite = data_integrity()
    suite_result = integ_suite.run(ds)
    
    # Save results
    output_dir = "tests/validation_reports"
    os.makedirs(output_dir, exist_ok=True)
    report_path = f"{output_dir}/data_integrity_report.html"
    suite_result.save_as_html(report_path)
    print(f"Validation Report saved to: {report_path}")
    
    # Optional: Fail if conditions not met (basic check)
    # This is a simplification; in a real CI, we might parse the JSON result.
    passed = suite_result.passed()
    print(f"DeepChecks Passed: {passed}")
    
    return passed

if __name__ == "__main__":
    run_data_validation()
