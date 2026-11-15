
from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"
REPORT_FOLDER = PROJECT_ROOT / "reports"


# --------------------------------------------------
# 2. LOAD CLEANED SALES DATA
# --------------------------------------------------

def load_product_data():
    """Load cleaned sales data for product analysis."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_FILE}\n"
            "Please complete Stage 3 before running Stage 5."
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "StockCode",
        "Description",
        "Quantity",
        "UnitPrice",
        "Revenue"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Convert numeric columns safely.
    data["Quantity"] = pd.to_numeric(
        data["Quantity"], errors="coerce"
    )

    data["UnitPrice"] = pd.to_numeric(
        data["UnitPrice"], errors="coerce"
    )

    data["Revenue"] = pd.to_numeric(
        data["Revenue"], errors="coerce"
    )

    # Remove rows with invalid product or sales information.
    data = data.dropna(
        subset=["StockCode", "Quantity", "UnitPrice", "Revenue"]
    )

    # Keep only actual positive sales.
    data = data[
        (data["Quantity"] > 0) &
        (data["UnitPrice"] > 0) &
        (data["Revenue"] > 0)
    ].copy()

    # Replace missing descriptions with a readable label.
    data["Description"] = (
        data["Description"]
        .fillna("Unknown Product")
        .astype(str)
        .str.strip()
    )

    data.loc[
        data["Description"] == "",
        "Description"
    ] = "Unknown Product"

    if data.empty:
        raise ValueError("No valid product sales records found.")

    return data


# --------------------------------------------------
# 3. GROUP SALES BY PRODUCT
# --------------------------------------------------

def create_product_summary(data):
    """Calculate revenue and quantity for each product."""

    product_summary = (
        data.groupby(
            ["StockCode", "Description"],
            as_index=False
        )
        .agg(
            TotalRevenue=("Revenue", "sum"),
            TotalQuantitySold=("Quantity", "sum"),
            NumberOfTransactions=("InvoiceNo", "nunique")
            if "InvoiceNo" in data.columns
            else ("Quantity", "count"),
            AverageUnitPrice=("UnitPrice", "mean")
        )
    )

    product_summary = product_summary.sort_values(
        by="TotalRevenue",
        ascending=False
    )

    return product_summary


# --------------------------------------------------
# 4. TOP 10 PRODUCTS BY REVENUE
# --------------------------------------------------

def get_top_products_by_revenue(product_summary):
    """Find products generating the highest revenue."""

    return (
        product_summary
        .sort_values("TotalRevenue", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 5. TOP 10 PRODUCTS BY QUANTITY
# --------------------------------------------------

def get_top_products_by_quantity(product_summary):
    """Find products with the highest quantity sold."""

    return (
        product_summary
        .sort_values("TotalQuantitySold", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 6. LOWEST 10 PRODUCTS BY REVENUE
# --------------------------------------------------

def get_least_selling_products(product_summary):
    """Find products with the lowest total revenue."""

    return (
        product_summary
        .sort_values("TotalRevenue", ascending=True)
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 7. OVERALL PRODUCT METRICS
# --------------------------------------------------

def calculate_product_metrics(data, product_summary):
    """Calculate overall product performance metrics."""

    total_products = product_summary["StockCode"].nunique()

    total_quantity = data["Quantity"].sum()

    total_revenue = data["Revenue"].sum()

    average_product_revenue = (
        product_summary["TotalRevenue"].mean()
    )

    highest_revenue_product = (
        product_summary.iloc[0]["Description"]
    )

    highest_revenue = (
        product_summary.iloc[0]["TotalRevenue"]
    )

    metrics = pd.DataFrame({
        "Metric": [
            "Total Unique Products",
            "Total Quantity Sold",
            "Total Product Revenue",
            "Average Revenue Per Product",
            "Highest Revenue Product",
            "Highest Product Revenue"
        ],
        "Value": [
            total_products,
            total_quantity,
            round(total_revenue, 2),
            round(average_product_revenue, 2),
            highest_revenue_product,
            round(highest_revenue, 2)
        ]
    })

    return metrics


# --------------------------------------------------
# 8. SAVE PRODUCT REPORTS
# --------------------------------------------------

def save_product_reports(
    product_summary,
    top_revenue,
    top_quantity,
    least_selling,
    metrics
):
    """Save all product analysis reports as CSV files."""

    REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    product_summary.to_csv(
        REPORT_FOLDER / "product_summary.csv",
        index=False
    )

    top_revenue.to_csv(
        REPORT_FOLDER / "top_products_by_revenue.csv",
        index=False
    )

    top_quantity.to_csv(
        REPORT_FOLDER / "top_products_by_quantity.csv",
        index=False
    )

    least_selling.to_csv(
        REPORT_FOLDER / "least_selling_products.csv",
        index=False
    )

    metrics.to_csv(
        REPORT_FOLDER / "product_metrics.csv",
        index=False
    )

    print("\nProduct analysis reports saved successfully!")


# --------------------------------------------------
# 9. DISPLAY RESULTS
# --------------------------------------------------

def display_results(
    product_summary,
    top_revenue,
    top_quantity,
    least_selling,
    metrics
):
    """Display important product analysis results."""

    print("\n======================================")
    print("       PRODUCT ANALYSIS RESULTS")
    print("======================================")

    print("\nOVERALL PRODUCT METRICS")
    print(metrics.to_string(index=False))

    print("\nTOP 10 PRODUCTS BY REVENUE")
    print(top_revenue.to_string(index=False))

    print("\nTOP 10 PRODUCTS BY QUANTITY SOLD")
    print(top_quantity.to_string(index=False))

    print("\n10 LOWEST PRODUCTS BY REVENUE")
    print(least_selling.to_string(index=False))

    print("\nTotal product records analysed:", len(product_summary))


# --------------------------------------------------
# 10. MAIN FUNCTION
# --------------------------------------------------

def main():

    try:
        print("Loading cleaned sales dataset...")

        data = load_product_data()

        print("Dataset loaded successfully!")
        print("Sales records available:", len(data))

        print("\nAnalysing product performance...")

        product_summary = create_product_summary(data)

        top_revenue = get_top_products_by_revenue(
            product_summary
        )

        top_quantity = get_top_products_by_quantity(
            product_summary
        )

        least_selling = get_least_selling_products(
            product_summary
        )

        metrics = calculate_product_metrics(
            data,
            product_summary
        )

        save_product_reports(
            product_summary,
            top_revenue,
            top_quantity,
            least_selling,
            metrics
        )

        display_results(
            product_summary,
            top_revenue,
            top_quantity,
            least_selling,
            metrics
        )

        print("\n======================================")
        print("STAGE 5 PRODUCT ANALYSIS COMPLETED")
        print("======================================")

    except Exception as error:
        print("\nERROR:", error)


if __name__ == "__main__":
    main()
