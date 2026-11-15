
from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_sales.csv"
)

REPORT_FOLDER = PROJECT_ROOT / "reports"


# --------------------------------------------------
# 2. LOAD COUNTRY SALES DATA
# --------------------------------------------------

def load_country_data():
    """Load cleaned sales data for country analysis."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "Country",
        "InvoiceNo",
        "Quantity",
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
        data["Quantity"],
        errors="coerce"
    )

    data["Revenue"] = pd.to_numeric(
        data["Revenue"],
        errors="coerce"
    )

    # Remove records with invalid sales information.
    data = data.dropna(
        subset=[
            "Country",
            "InvoiceNo",
            "Quantity",
            "Revenue"
        ]
    ).copy()

    # Clean country names.
    data["Country"] = (
        data["Country"]
        .astype(str)
        .str.strip()
    )

    data = data[data["Country"] != ""]

    # Keep valid positive sales.
    data = data[
        (data["Quantity"] > 0) &
        (data["Revenue"] > 0)
    ].copy()

    if data.empty:
        raise ValueError(
            "No valid country sales records found."
        )

    return data


# --------------------------------------------------
# 3. CREATE COUNTRY-WISE SUMMARY
# --------------------------------------------------

def create_country_summary(data):
    """Calculate sales performance for each country."""

    country_summary = (
        data.groupby("Country")
        .agg(
            TotalRevenue=("Revenue", "sum"),
            TotalQuantitySold=("Quantity", "sum"),
            TotalOrders=("InvoiceNo", "nunique"),
            TotalTransactions=("InvoiceNo", "count"),
            AverageUnitRevenue=("Revenue", "mean")
        )
        .reset_index()
    )

    # Calculate average revenue per order.
    country_summary["AverageOrderValue"] = (
        country_summary["TotalRevenue"]
        / country_summary["TotalOrders"]
    )

    # Calculate each country's share of total revenue.
    total_revenue = country_summary["TotalRevenue"].sum()

    if total_revenue > 0:
        country_summary["RevenuePercentage"] = (
            country_summary["TotalRevenue"]
            / total_revenue
            * 100
        )
    else:
        country_summary["RevenuePercentage"] = 0

    country_summary = country_summary.sort_values(
        by="TotalRevenue",
        ascending=False
    )

    return country_summary


# --------------------------------------------------
# 4. TOP 10 COUNTRIES BY REVENUE
# --------------------------------------------------

def get_top_countries_by_revenue(country_summary):
    """Find countries generating the highest revenue."""

    return (
        country_summary
        .sort_values(
            by="TotalRevenue",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 5. TOP 10 COUNTRIES BY NUMBER OF ORDERS
# --------------------------------------------------

def get_top_countries_by_orders(country_summary):
    """Find countries with the most unique orders."""

    return (
        country_summary
        .sort_values(
            by="TotalOrders",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 6. TOP 10 COUNTRIES BY QUANTITY SOLD
# --------------------------------------------------

def get_top_countries_by_quantity(country_summary):
    """Find countries with the highest sales quantity."""

    return (
        country_summary
        .sort_values(
            by="TotalQuantitySold",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 7. CALCULATE COUNTRY PERFORMANCE METRICS
# --------------------------------------------------

def calculate_country_metrics(data, country_summary):
    """Calculate overall geographical sales metrics."""

    total_countries = country_summary["Country"].nunique()

    total_revenue = data["Revenue"].sum()

    total_quantity = data["Quantity"].sum()

    total_orders = data["InvoiceNo"].nunique()

    highest_revenue_country = (
        country_summary.iloc[0]["Country"]
    )

    highest_country_revenue = (
        country_summary.iloc[0]["TotalRevenue"]
    )

    highest_order_country = (
        country_summary
        .sort_values("TotalOrders", ascending=False)
        .iloc[0]["Country"]
    )

    metrics = pd.DataFrame({
        "Metric": [
            "Total Countries",
            "Total Revenue",
            "Total Quantity Sold",
            "Total Unique Orders",
            "Highest Revenue Country",
            "Highest Country Revenue",
            "Highest Order Volume Country"
        ],
        "Value": [
            total_countries,
            round(total_revenue, 2),
            total_quantity,
            total_orders,
            highest_revenue_country,
            round(highest_country_revenue, 2),
            highest_order_country
        ]
    })

    return metrics


# --------------------------------------------------
# 8. SAVE COUNTRY ANALYSIS REPORTS
# --------------------------------------------------

def save_country_reports(
    country_summary,
    top_revenue,
    top_orders,
    top_quantity,
    metrics
):
    """Save all country analysis reports as CSV files."""

    REPORT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    country_summary.to_csv(
        REPORT_FOLDER / "country_summary.csv",
        index=False
    )

    top_revenue.to_csv(
        REPORT_FOLDER / "top_countries_by_revenue.csv",
        index=False
    )

    top_orders.to_csv(
        REPORT_FOLDER / "top_countries_by_orders.csv",
        index=False
    )

    top_quantity.to_csv(
        REPORT_FOLDER / "top_countries_by_quantity.csv",
        index=False
    )

    metrics.to_csv(
        REPORT_FOLDER / "country_metrics.csv",
        index=False
    )

    print("\nCountry analysis reports saved successfully!")


# --------------------------------------------------
# 9. DISPLAY COUNTRY ANALYSIS RESULTS
# --------------------------------------------------

def display_results(
    country_summary,
    top_revenue,
    top_orders,
    top_quantity,
    metrics
):
    """Display important country analysis results."""

    print("\n======================================")
    print("        COUNTRY ANALYSIS RESULTS")
    print("======================================")

    print("\nOVERALL COUNTRY METRICS")
    print(metrics.to_string(index=False))

    print("\nTOP 10 COUNTRIES BY REVENUE")
    print(top_revenue.to_string(index=False))

    print("\nTOP 10 COUNTRIES BY NUMBER OF ORDERS")
    print(top_orders.to_string(index=False))

    print("\nTOP 10 COUNTRIES BY QUANTITY SOLD")
    print(top_quantity.to_string(index=False))

    print(
        "\nTotal countries analysed:",
        len(country_summary)
    )


# --------------------------------------------------
# 10. MAIN FUNCTION
# --------------------------------------------------

def main():

    try:
        print("Loading cleaned country sales dataset...")

        data = load_country_data()

        print("Dataset loaded successfully!")
        print("Valid sales records:", len(data))

        print("\nAnalysing country-wise sales performance...")

        country_summary = create_country_summary(data)

        top_revenue = get_top_countries_by_revenue(
            country_summary
        )

        top_orders = get_top_countries_by_orders(
            country_summary
        )

        top_quantity = get_top_countries_by_quantity(
            country_summary
        )

        metrics = calculate_country_metrics(
            data,
            country_summary
        )

        save_country_reports(
            country_summary,
            top_revenue,
            top_orders,
            top_quantity,
            metrics
        )

        display_results(
            country_summary,
            top_revenue,
            top_orders,
            top_quantity,
            metrics
        )

        print("\n======================================")
        print("STAGE 7 COUNTRY ANALYSIS COMPLETED")
        print("======================================")

    except Exception as error:
        print("\nERROR:", error)


if __name__ == "__main__":
    main()
