
# ============================================================
# CCW331 BUSINESS ANALYTICS MINI PROJECT
# Stage 3: Data Cleaning and Preprocessing
# ============================================================

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# 1. PROJECT PATHS
# ------------------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_FOLDER / "data" / "raw" / "Online Retail.xlsx"

PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"

SALES_FILE = PROCESSED_FOLDER / "cleaned_sales.csv"
RETURNS_FILE = PROCESSED_FOLDER / "returns.csv"
CANCELLED_FILE = PROCESSED_FOLDER / "cancelled_transactions.csv"
INVALID_FILE = PROCESSED_FOLDER / "invalid_records.csv"
REPORT_FILE = PROCESSED_FOLDER / "cleaning_report.csv"


# ------------------------------------------------------------
# 2. LOAD DATASET
# ------------------------------------------------------------

def load_raw_data():

    print("\nSTAGE 3: DATA CLEANING AND PREPROCESSING")
    print("=" * 55)

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}"
        )

    data = pd.read_excel(RAW_FILE)

    print("\nOriginal dataset loaded successfully!")
    print("Original records:", len(data))

    return data


# ------------------------------------------------------------
# 3. CLEAN DATASET
# ------------------------------------------------------------

def clean_dataset(data):

    original_count = len(data)

    # Store cleaning statistics
    report = []

    def add_report(step, before, after):
        report.append({
            "Cleaning Step": step,
            "Records Before": before,
            "Records After": after,
            "Records Removed": before - after
        })

    # --------------------------------------------------------
    # STEP 1: REMOVE DUPLICATES
    # --------------------------------------------------------

    before = len(data)

    data = data.drop_duplicates().copy()

    add_report("Duplicate removal", before, len(data))

    print("\nDuplicate records removed:",
          before - len(data))

    # --------------------------------------------------------
    # STEP 2: CLEAN COLUMN FORMATS
    # --------------------------------------------------------

    data.columns = data.columns.str.strip()

    data["InvoiceNo"] = data["InvoiceNo"].astype("string").str.strip()
    data["StockCode"] = data["StockCode"].astype("string").str.strip()

    data["Description"] = (
        data["Description"]
        .astype("string")
        .str.strip()
    )

    data["Country"] = (
        data["Country"]
        .astype("string")
        .str.strip()
    )

    # Convert numeric columns safely
    data["Quantity"] = pd.to_numeric(
        data["Quantity"], errors="coerce"
    )

    data["UnitPrice"] = pd.to_numeric(
        data["UnitPrice"], errors="coerce"
    )

    data["CustomerID"] = pd.to_numeric(
        data["CustomerID"], errors="coerce"
    )

    # Convert invoice date
    data["InvoiceDate"] = pd.to_datetime(
        data["InvoiceDate"], errors="coerce"
    )

    # --------------------------------------------------------
    # STEP 3: IDENTIFY INVALID RECORDS
    # --------------------------------------------------------

    invalid_mask = (
        data["InvoiceNo"].isna()
        | data["InvoiceNo"].eq("")
        | data["StockCode"].isna()
        | data["Quantity"].isna()
        | data["UnitPrice"].isna()
        | data["InvoiceDate"].isna()
    )

    invalid_records = data[invalid_mask].copy()

    data = data[~invalid_mask].copy()

    add_report(
        "Missing essential fields or invalid formats",
        len(data) + len(invalid_records),
        len(data)
    )

    print("Invalid records identified:",
          len(invalid_records))

    # --------------------------------------------------------
    # STEP 4: IDENTIFY CANCELLED INVOICES
    # --------------------------------------------------------

    cancellation_mask = (
        data["InvoiceNo"].str.upper().str.startswith("C")
    )

    cancelled_transactions = data[
        cancellation_mask
    ].copy()

    data = data[~cancellation_mask].copy()

    print("Cancelled transaction records:",
          len(cancelled_transactions))

    # --------------------------------------------------------
    # STEP 5: IDENTIFY RETURNS
    # --------------------------------------------------------

    return_mask = data["Quantity"] < 0

    returns = data[return_mask].copy()

    data = data[~return_mask].copy()

    # Calculate positive return quantity and value
    returns["ReturnQuantity"] = returns["Quantity"].abs()

    returns["ReturnValue"] = (
        returns["ReturnQuantity"] * returns["UnitPrice"]
    )

    print("Return transaction records:", len(returns))

    # --------------------------------------------------------
    # STEP 6: REMOVE INVALID SALES PRICES
    # --------------------------------------------------------

    invalid_price_mask = data["UnitPrice"] <= 0

    invalid_prices = data[invalid_price_mask].copy()

    data = data[~invalid_price_mask].copy()

    invalid_prices["InvalidReason"] = "Zero or negative unit price"

    invalid_records["InvalidReason"] = (
        "Missing essential field or invalid format"
    )

    invalid_records = pd.concat(
        [invalid_records, invalid_prices],
        ignore_index=True
    )

    # --------------------------------------------------------
    # STEP 7: REMOVE ZERO QUANTITY RECORDS
    # --------------------------------------------------------

    zero_quantity_mask = data["Quantity"] == 0

    zero_quantity_records = data[
        zero_quantity_mask
    ].copy()

    data = data[~zero_quantity_mask].copy()

    zero_quantity_records["InvalidReason"] = (
        "Zero quantity"
    )

    invalid_records = pd.concat(
        [invalid_records, zero_quantity_records],
        ignore_index=True
    )

    # --------------------------------------------------------
    # STEP 8: HANDLE MISSING DESCRIPTIONS AND COUNTRIES
    # --------------------------------------------------------

    data["Description"] = (
        data["Description"].fillna("Unknown Product")
    )

    data["Country"] = (
        data["Country"].fillna("Unknown Country")
    )

    # CustomerID is intentionally not filled with fake IDs.
    # Transactions without CustomerID remain available
    # for sales analysis but are excluded from customer analysis.

    # --------------------------------------------------------
    # STEP 9: CALCULATE REVENUE
    # --------------------------------------------------------

    data["Revenue"] = (
        data["Quantity"] * data["UnitPrice"]
    )

    # Add useful date columns
    data["Year"] = data["InvoiceDate"].dt.year

    data["Month"] = data["InvoiceDate"].dt.month

    data["MonthName"] = data["InvoiceDate"].dt.strftime("%B")

    data["Day"] = data["InvoiceDate"].dt.day

    data["DayName"] = data["InvoiceDate"].dt.day_name()

    # --------------------------------------------------------
    # STEP 10: SORT DATA
    # --------------------------------------------------------

    data = data.sort_values(
        by="InvoiceDate"
    ).reset_index(drop=True)

    returns = returns.sort_values(
        by="InvoiceDate"
    ).reset_index(drop=True)

    cancelled_transactions = cancelled_transactions.reset_index(
        drop=True
    )

    invalid_records = invalid_records.reset_index(
        drop=True
    )

    print("\nData cleaning completed!")

    print("Original records:", original_count)
    print("Clean sales records:", len(data))
    print("Return records:", len(returns))
    print("Cancelled records:", len(cancelled_transactions))
    print("Invalid records:", len(invalid_records))

    return (
        data,
        returns,
        cancelled_transactions,
        invalid_records,
        report
    )


# ------------------------------------------------------------
# 4. SAVE PROCESSED DATA
# ------------------------------------------------------------

def save_processed_data(
    sales,
    returns,
    cancelled,
    invalid,
    report
):

    PROCESSED_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    sales.to_csv(SALES_FILE, index=False)

    returns.to_csv(RETURNS_FILE, index=False)

    cancelled.to_csv(CANCELLED_FILE, index=False)

    invalid.to_csv(INVALID_FILE, index=False)

    pd.DataFrame(report).to_csv(
        REPORT_FILE,
        index=False
    )

    print("\nPROCESSED FILES SAVED")
    print("=" * 40)

    print("Sales:", SALES_FILE)
    print("Returns:", RETURNS_FILE)
    print("Cancelled:", CANCELLED_FILE)
    print("Invalid:", INVALID_FILE)
    print("Cleaning report:", REPORT_FILE)


# ------------------------------------------------------------
# 5. MAIN PROGRAM
# ------------------------------------------------------------

def main():

    try:

        # Load original dataset
        raw_data = load_raw_data()

        # Perform data cleaning
        (
            sales,
            returns,
            cancelled,
            invalid,
            report
        ) = clean_dataset(raw_data)

        # Save all processed files
        save_processed_data(
            sales,
            returns,
            cancelled,
            invalid,
            report
        )

        print("\nSTAGE 3 COMPLETED SUCCESSFULLY!")

        print("\nFinal Sales Dataset Preview:")
        print(sales.head(5).to_string())

        print("\nFinal Sales Dataset Shape:")
        print(sales.shape)

    except Exception as error:

        print("\nDATA CLEANING ERROR:")
        print(error)


if __name__ == "__main__":
    main()
