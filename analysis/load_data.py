
# CCW331 Business Analytics
# Stage 2: Load Online Retail Dataset

import pandas as pd
from pathlib import Path

# Find the main project folder
PROJECT_FOLDER = Path(__file__).resolve().parents[1]

# Dataset location
DATASET_PATH = PROJECT_FOLDER / "data" / "raw" / "Online Retail.xlsx"


def load_dataset():

    print("\nONLINE RETAIL BUSINESS ANALYTICS")
    print("=" * 45)

    # Check whether dataset exists
    if not DATASET_PATH.exists():
        print("ERROR: Dataset file not found!")
        print("Expected location:", DATASET_PATH)
        return None

    print("\nLoading dataset...")

    try:
        # Read Excel dataset
        data = pd.read_excel(DATASET_PATH)

        print("\nDataset loaded successfully!")

        # Display number of rows and columns
        print("\n1. DATASET SIZE")
        print("Rows:", data.shape[0])
        print("Columns:", data.shape[1])

        # Display column names
        print("\n2. COLUMN NAMES")
        print(data.columns.tolist())

        # Display first 10 records
        print("\n3. FIRST 10 RECORDS")
        print(data.head(10).to_string())

        # Display dataset information
        print("\n4. DATASET INFORMATION")
        data.info()

        # Display missing values
        print("\n5. MISSING VALUES")
        print(data.isnull().sum())

        # Display basic statistics
        print("\n6. STATISTICAL SUMMARY")
        print(data.describe().to_string())

        return data

    except Exception as error:
        print("\nERROR WHILE LOADING DATASET")
        print(error)
        return None


if __name__ == "__main__":
    retail_data = load_dataset()

    if retail_data is not None:
        print("\nStage 2 dataset loading completed!")
