
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
# 2. LOAD CUSTOMER DATA
# --------------------------------------------------

def load_customer_data():
    """Load cleaned sales data for customer analysis."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "CustomerID",
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

    # Convert numeric columns.
    data["CustomerID"] = pd.to_numeric(
        data["CustomerID"],
        errors="coerce"
    )

    data["Quantity"] = pd.to_numeric(
        data["Quantity"],
        errors="coerce"
    )

    data["Revenue"] = pd.to_numeric(
        data["Revenue"],
        errors="coerce"
    )

    # Convert invoice dates if available.
    if "InvoiceDate" in data.columns:
        data["InvoiceDate"] = pd.to_datetime(
            data["InvoiceDate"],
            errors="coerce"
        )

    # Remove records without identifiable customers.
    data = data.dropna(
        subset=[
            "CustomerID",
            "InvoiceNo",
            "Quantity",
            "Revenue"
        ]
    ).copy()

    # Keep valid positive sales.
    data = data[
        (data["Quantity"] > 0) &
        (data["Revenue"] > 0)
    ].copy()

    if data.empty:
        raise ValueError(
            "No valid customer sales records found."
        )

    return data


# --------------------------------------------------
# 3. CREATE CUSTOMER SUMMARY
# --------------------------------------------------

def create_customer_summary(data):
    """Calculate sales and purchasing behaviour per customer."""

    aggregation = {
        "TotalRevenue": ("Revenue", "sum"),
        "TotalQuantityPurchased": ("Quantity", "sum"),
        "TotalOrders": ("InvoiceNo", "nunique"),
        "AverageTransactionValue": ("Revenue", "mean")
    }

    # Add first and last purchase dates when available.
    if "InvoiceDate" in data.columns:
        aggregation["FirstPurchase"] = (
            "InvoiceDate", "min"
        )

        aggregation["LastPurchase"] = (
            "InvoiceDate", "max"
        )

    customer_summary = (
        data.groupby("CustomerID")
        .agg(**aggregation)
        .reset_index()
    )

    # Calculate average order value per customer.
    customer_summary["AverageOrderValue"] = (
        customer_summary["TotalRevenue"]
        / customer_summary["TotalOrders"]
    )

    # Identify repeat customers.
    customer_summary["CustomerType"] = (
        customer_summary["TotalOrders"]
        .apply(
            lambda orders:
            "Repeat Customer"
            if orders > 1
            else "One-time Customer"
        )
    )

    customer_summary = customer_summary.sort_values(
        by="TotalRevenue",
        ascending=False
    )

    return customer_summary


# --------------------------------------------------
# 4. TOP CUSTOMERS BY REVENUE
# --------------------------------------------------

def get_top_customers_by_revenue(customer_summary):
    """Find the 10 customers who spend the most."""

    return (
        customer_summary
        .sort_values(
            by="TotalRevenue",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 5. TOP CUSTOMERS BY NUMBER OF ORDERS
# --------------------------------------------------

def get_top_customers_by_orders(customer_summary):
    """Find customers who place the most orders."""

    return (
        customer_summary
        .sort_values(
            by=["TotalOrders", "TotalRevenue"],
            ascending=[False, False]
        )
        .head(10)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 6. IDENTIFY REPEAT CUSTOMERS
# --------------------------------------------------

def get_repeat_customers(customer_summary):
    """Find customers who have placed multiple orders."""

    repeat_customers = customer_summary[
        customer_summary["TotalOrders"] > 1
    ].copy()

    return (
        repeat_customers
        .sort_values(
            by="TotalOrders",
            ascending=False
        )
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 7. CALCULATE CUSTOMER METRICS
# --------------------------------------------------

def calculate_customer_metrics(data, customer_summary):
    """Calculate overall customer performance metrics."""

    total_customers = len(customer_summary)

    repeat_customer_count = (
        customer_summary["TotalOrders"] > 1
    ).sum()

    one_time_customer_count = (
        customer_summary["TotalOrders"] == 1
    ).sum()

    total_customer_revenue = (
        customer_summary["TotalRevenue"].sum()
    )

    total_orders = (
        customer_summary["TotalOrders"].sum()
    )

    average_customer_spending = (
        customer_summary["TotalRevenue"].mean()
    )

    repeat_customer_percentage = (
        repeat_customer_count / total_customers * 100
        if total_customers > 0
        else 0
    )

    average_order_value = (
        total_customer_revenue / total_orders
        if total_orders > 0
        else 0
    )

    metrics = pd.DataFrame({
        "Metric": [
            "Total Identified Customers",
            "Repeat Customers",
            "One-time Customers",
            "Repeat Customer Percentage",
            "Total Customer Revenue",
            "Total Customer Orders",
            "Average Customer Spending",
            "Average Order Value"
        ],
        "Value": [
            total_customers,
            repeat_customer_count,
            one_time_customer_count,
            round(repeat_customer_percentage, 2),
            round(total_customer_revenue, 2),
            total_orders,
            round(average_customer_spending, 2),
            round(average_order_value, 2)
        ]
    })

    return metrics


# --------------------------------------------------
# 8. SAVE CUSTOMER REPORTS
# --------------------------------------------------

def save_customer_reports(
    customer_summary,
    top_revenue,
    top_orders,
    repeat_customers,
    metrics
):
    """Save customer analysis reports as CSV files."""

    REPORT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    customer_summary.to_csv(
        REPORT_FOLDER / "customer_summary.csv",
        index=False
    )

    top_revenue.to_csv(
        REPORT_FOLDER / "top_customers_by_revenue.csv",
        index=False
    )

    top_orders.to_csv(
        REPORT_FOLDER / "top_customers_by_orders.csv",
        index=False
    )

    repeat_customers.to_csv(
        REPORT_FOLDER / "repeat_customers.csv",
        index=False
    )

    metrics.to_csv(
        REPORT_FOLDER / "customer_metrics.csv",
        index=False
    )

    print("\nCustomer analysis reports saved successfully!")


# --------------------------------------------------
# 9. DISPLAY CUSTOMER RESULTS
# --------------------------------------------------

def display_results(
    customer_summary,
    top_revenue,
    top_orders,
    repeat_customers,
    metrics
):
    """Display customer analysis results."""

    print("\n======================================")
    print("       CUSTOMER ANALYSIS RESULTS")
    print("======================================")

    print("\nOVERALL CUSTOMER METRICS")
    print(metrics.to_string(index=False))

    print("\nTOP 10 CUSTOMERS BY REVENUE")
    print(top_revenue.to_string(index=False))

    print("\nTOP 10 CUSTOMERS BY NUMBER OF ORDERS")
    print(top_orders.to_string(index=False))

    print("\nREPEAT CUSTOMERS")
    print(repeat_customers.head(10).to_string(index=False))

    print(
        "\nTotal identified customers:",
        len(customer_summary)
    )

    print(
        "Total repeat customers:",
        len(repeat_customers)
    )


# --------------------------------------------------
# 10. MAIN FUNCTION
# --------------------------------------------------

def main():

    try:
        print("Loading cleaned customer dataset...")

        data = load_customer_data()

        print("Dataset loaded successfully!")
        print("Valid sales records:", len(data))

        print("\nAnalysing customer behaviour...")

        customer_summary = create_customer_summary(data)

        top_revenue = get_top_customers_by_revenue(
            customer_summary
        )

        top_orders = get_top_customers_by_orders(
            customer_summary
        )

        repeat_customers = get_repeat_customers(
            customer_summary
        )

        metrics = calculate_customer_metrics(
            data,
            customer_summary
        )

        save_customer_reports(
            customer_summary,
            top_revenue,
            top_orders,
            repeat_customers,
            metrics
        )

        display_results(
            customer_summary,
            top_revenue,
            top_orders,
            repeat_customers,
            metrics
        )

        print("\n======================================")
        print("STAGE 6 CUSTOMER ANALYSIS COMPLETED")
        print("======================================")

    except Exception as error:
        print("\nERROR:", error)


if __name__ == "__main__":
    main()
