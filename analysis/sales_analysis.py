
# ============================================================
# CCW331 BUSINESS ANALYTICS MINI PROJECT
# Stage 4: Sales Analysis and Business Performance
# ============================================================

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# 1. PROJECT PATHS
# ------------------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parents[1]

PROCESSED_FOLDER = PROJECT_FOLDER / "data" / "processed"

SALES_FILE = PROCESSED_FOLDER / "cleaned_sales.csv"

RETURNS_FILE = PROCESSED_FOLDER / "returns.csv"

CANCELLED_FILE = (
    PROCESSED_FOLDER / "cancelled_transactions.csv"
)

REPORT_FOLDER = PROJECT_FOLDER / "reports"


# ------------------------------------------------------------
# 2. LOAD CLEANED SALES DATA
# ------------------------------------------------------------

def load_sales_data():

    print("\nSTAGE 4: SALES ANALYSIS")
    print("=" * 55)

    if not SALES_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned sales dataset not found: {SALES_FILE}"
        )

    data = pd.read_csv(SALES_FILE)

    required_columns = [
        "InvoiceNo",
        "Quantity",
        "UnitPrice",
        "InvoiceDate",
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

    # Convert columns into correct data types
    data["InvoiceDate"] = pd.to_datetime(
        data["InvoiceDate"],
        errors="coerce"
    )

    data["Quantity"] = pd.to_numeric(
        data["Quantity"],
        errors="coerce"
    )

    data["UnitPrice"] = pd.to_numeric(
        data["UnitPrice"],
        errors="coerce"
    )

    # Calculate revenue again to verify consistency
    data["Revenue"] = (
        data["Quantity"] * data["UnitPrice"]
    )

    # Remove rows that cannot be used in sales calculations
    data = data.dropna(
        subset=[
            "InvoiceNo",
            "InvoiceDate",
            "Quantity",
            "UnitPrice",
            "Revenue"
        ]
    )

    data = data[
        (data["Quantity"] > 0)
        & (data["UnitPrice"] > 0)
    ].copy()

    if data.empty:
        raise ValueError(
            "No valid sales records available for analysis."
        )

    print("\nSales dataset loaded successfully!")

    print("Total transaction records:", len(data))

    return data


# ------------------------------------------------------------
# 3. CALCULATE MAIN BUSINESS METRICS
# ------------------------------------------------------------

def calculate_sales_metrics(data):

    print("\n1. MAIN BUSINESS METRICS")
    print("-" * 45)

    total_revenue = data["Revenue"].sum()

    total_orders = data["InvoiceNo"].nunique()

    total_quantity = data["Quantity"].sum()

    total_products = data["StockCode"].nunique()

    total_customers = (
        data["CustomerID"].nunique()
        if "CustomerID" in data.columns
        else 0
    )

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    metrics = {
        "Total Revenue": total_revenue,
        "Total Orders": total_orders,
        "Total Quantity Sold": total_quantity,
        "Unique Products": total_products,
        "Unique Customers": total_customers,
        "Average Order Value": average_order_value
    }

    for name, value in metrics.items():

        if name in [
            "Total Revenue",
            "Average Order Value"
        ]:
            print(f"{name}: GBP {value:,.2f}")

        else:
            print(f"{name}: {value:,.0f}")

    return metrics


# ------------------------------------------------------------
# 4. CREATE INVOICE-WISE SALES REPORT
# ------------------------------------------------------------

def create_invoice_report(data):

    invoice_report = (
        data.groupby("InvoiceNo")
        .agg(
            OrderDate=("InvoiceDate", "min"),
            OrderRevenue=("Revenue", "sum"),
            ItemsPurchased=("Quantity", "sum")
        )
        .reset_index()
    )

    if "CustomerID" in data.columns:
        customer_info = (
            data.groupby("InvoiceNo")["CustomerID"]
            .first()
            .reset_index()
        )

        invoice_report = invoice_report.merge(
            customer_info,
            on="InvoiceNo",
            how="left"
        )

    return invoice_report


# ------------------------------------------------------------
# 5. MONTHLY SALES ANALYSIS
# ------------------------------------------------------------

def monthly_sales_analysis(data):

    print("\n2. MONTHLY SALES ANALYSIS")
    print("-" * 45)

    monthly_data = data.copy()

    monthly_data["Month"] = (
        monthly_data["InvoiceDate"].dt.to_period("M")
    )

    monthly_report = (
        monthly_data.groupby("Month")
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            QuantitySold=("Quantity", "sum")
        )
        .reset_index()
    )

    monthly_report["Month"] = (
        monthly_report["Month"].astype(str)
    )

    monthly_report["AverageOrderValue"] = (
        monthly_report["Revenue"]
        / monthly_report["Orders"]
    )

    monthly_report["RevenueGrowthPercent"] = (
        monthly_report["Revenue"].pct_change() * 100
    )

    monthly_report["RevenueGrowthPercent"] = (
        monthly_report["RevenueGrowthPercent"].round(2)
    )

    monthly_report["RevenueGrowthPercent"] = (
        monthly_report["RevenueGrowthPercent"].fillna(0)
    )

    print(monthly_report.to_string(index=False))

    best_month = monthly_report.loc[
        monthly_report["Revenue"].idxmax()
    ]

    print("\nHighest Revenue Month:", best_month["Month"])

    print(
        "Highest Monthly Revenue: GBP "
        f"{best_month['Revenue']:,.2f}"
    )

    return monthly_report


# ------------------------------------------------------------
# 6. DAILY SALES ANALYSIS
# ------------------------------------------------------------

def daily_sales_analysis(data):

    print("\n3. DAILY SALES ANALYSIS")
    print("-" * 45)

    daily_data = data.copy()

    daily_data["Date"] = (
        daily_data["InvoiceDate"].dt.date
    )

    daily_report = (
        daily_data.groupby("Date")
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            QuantitySold=("Quantity", "sum")
        )
        .reset_index()
    )

    daily_report["Date"] = (
        daily_report["Date"].astype(str)
    )

    print("\nFirst 10 Daily Records:")

    print(
        daily_report.head(10).to_string(index=False)
    )

    best_day = daily_report.loc[
        daily_report["Revenue"].idxmax()
    ]

    print("\nHighest Sales Date:", best_day["Date"])

    print(
        "Highest Daily Revenue: GBP "
        f"{best_day['Revenue']:,.2f}"
    )

    return daily_report


# ------------------------------------------------------------
# 7. RETURN AND CANCELLATION SUMMARY
# ------------------------------------------------------------

def calculate_return_summary():

    summary = {
        "Return Records": 0,
        "Returned Quantity": 0,
        "Return Value": 0,
        "Cancelled Records": 0,
        "Cancelled Invoices": 0
    }

    if RETURNS_FILE.exists():

        returns = pd.read_csv(RETURNS_FILE)

        summary["Return Records"] = len(returns)

        if "ReturnQuantity" in returns.columns:
            summary["Returned Quantity"] = (
                returns["ReturnQuantity"].sum()
            )

        if "ReturnValue" in returns.columns:
            summary["Return Value"] = (
                returns["ReturnValue"].sum()
            )

    if CANCELLED_FILE.exists():

        cancelled = pd.read_csv(CANCELLED_FILE)

        summary["Cancelled Records"] = len(cancelled)

        if "InvoiceNo" in cancelled.columns:
            summary["Cancelled Invoices"] = (
                cancelled["InvoiceNo"].nunique()
            )

    print("\n4. RETURNS AND CANCELLATIONS")
    print("-" * 45)

    for name, value in summary.items():

        if name == "Return Value":
            print(f"{name}: GBP {value:,.2f}")
        else:
            print(f"{name}: {value:,.0f}")

    return summary


# ------------------------------------------------------------
# 8. SAVE SALES REPORTS
# ------------------------------------------------------------

def save_reports(
    metrics,
    invoice_report,
    monthly_report,
    daily_report,
    return_summary
):

    REPORT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save business metrics
    summary_report = pd.DataFrame(
        list(metrics.items()),
        columns=["Metric", "Value"]
    )

    summary_report = pd.concat(
        [
            summary_report,
            pd.DataFrame(
                list(return_summary.items()),
                columns=["Metric", "Value"]
            )
        ],
        ignore_index=True
    )

    summary_report.to_csv(
        REPORT_FOLDER / "sales_summary.csv",
        index=False
    )

    # Save invoice-wise analysis
    invoice_report.to_csv(
        REPORT_FOLDER / "invoice_sales.csv",
        index=False
    )

    # Save monthly analysis
    monthly_report.to_csv(
        REPORT_FOLDER / "monthly_sales.csv",
        index=False
    )

    # Save daily analysis
    daily_report.to_csv(
        REPORT_FOLDER / "daily_sales.csv",
        index=False
    )

    print("\n5. REPORTS SAVED SUCCESSFULLY")
    print("-" * 45)

    print("sales_summary.csv")
    print("invoice_sales.csv")
    print("monthly_sales.csv")
    print("daily_sales.csv")


# ------------------------------------------------------------
# 9. MAIN PROGRAM
# ------------------------------------------------------------

def main():

    try:

        # Load cleaned sales dataset
        sales_data = load_sales_data()

        # Calculate business metrics
        metrics = calculate_sales_metrics(
            sales_data
        )

        # Create invoice-wise report
        invoice_report = create_invoice_report(
            sales_data
        )

        # Monthly sales analysis
        monthly_report = monthly_sales_analysis(
            sales_data
        )

        # Daily sales analysis
        daily_report = daily_sales_analysis(
            sales_data
        )

        # Returns and cancellations
        return_summary = calculate_return_summary()

        # Save all reports
        save_reports(
            metrics,
            invoice_report,
            monthly_report,
            daily_report,
            return_summary
        )

        print("\n" + "=" * 55)
        print("STAGE 4 COMPLETED SUCCESSFULLY!")
        print("=" * 55)

    except Exception as error:

        print("\nSALES ANALYSIS ERROR:")
        print(error)


if __name__ == "__main__":
    main()
